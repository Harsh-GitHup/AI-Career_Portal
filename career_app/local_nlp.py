import logging
import re
from collections import Counter

from .models import CareerRole, CourseRecommendation, InterviewQuestion, RoleSkill

logger = logging.getLogger(__name__)

# Initialize ML Pipelines lazily so they don't block server startup
_nlp = None
_zero_shot = None


def get_spacy():
    global _nlp
    if _nlp is None:
        try:
            import spacy

            _nlp = spacy.load("en_core_web_sm")
        except Exception as e:  # noqa: BLE001
            logger.warning(f"SpaCy load error: {e}")
            return None
    return _nlp


def get_zero_shot():
    global _zero_shot
    if _zero_shot is None:
        try:
            from transformers import pipeline

            # We use a highly efficient model for fast CPU zero-shot classification
            _zero_shot = pipeline(
                "zero-shot-classification",
                model="typeform/distilbert-base-uncased-mnli",
            )
        except Exception as e:  # noqa: BLE001
            logger.warning(f"Transformers zero-shot load error: {e}")
            return None
    return _zero_shot


class LocalNLPResumeParser:
    """Custom Offline Advanced NLP Model for Resume Parsing using Deep Learning."""

    def __init__(self, text: str):
        self.text = text
        self.text_lower = text.lower()
        self.nlp = get_spacy()
        self.doc = self.nlp(text) if self.nlp else None

    def extract_name(self) -> str:
        # Use SpaCy NER to accurately locate the first PERSON entity
        blacklist = {
            "resume",
            "cv",
            "curriculum",
            "vitae",
            "html",
            "document",
            "profile",
        }
        if self.doc:
            for ent in self.doc.ents:
                if ent.label_ == "PERSON":
                    clean_name = re.sub(r"[^a-zA-Z\s]", "", ent.text).strip()
                    if (
                        len(clean_name) > 3
                        and len(clean_name) < 30
                        and clean_name.lower() not in blacklist
                    ):
                        return clean_name.title()

        # Basic parsing fallback if SpaCy fails or isn't loaded yet
        lines = [line.strip() for line in self.text.split("\n") if line.strip()]
        if not lines:
            return "Unknown Candidate"
        for line in lines[:5]:
            clean_name = re.sub(r"[^a-zA-Z\s]", "", line).strip()
            if (
                len(clean_name) > 3
                and len(clean_name) < 30
                and clean_name.lower() not in blacklist
            ):
                return clean_name.title()
        return "Unknown Candidate"

    def extract_skills(self) -> list[str]:
        found_skills = set()
        roles = CareerRole.objects.prefetch_related("skills").all()
        for role in roles:
            for skill_obj in role.skills.all():
                skill = skill_obj.skill_name
                if re.search(r"\b" + re.escape(skill.lower()) + r"\b", self.text_lower):
                    found_skills.add(skill.title())

        if not found_skills and self.doc:
            # Dynamically extract syntax Noun Chunks as skills using SpaCy
            stops = {"The", "And", "For", "With", "This", "That", "Are", "Was"}
            chunks = [
                chunk.text.title()
                for chunk in self.doc.noun_chunks
                if len(chunk.text.split()) < 3
            ]
            counts = Counter(chunks)
            found_skills = {
                w
                for w, c in counts.most_common(12)
                if w not in stops and not re.search(r"\d", w)
            }

        return list(found_skills)[:10]

    def determine_roles(self, skills: list[str]) -> list[str]:
        roles = CareerRole.objects.all()
        candidate_labels = [r.title for r in roles]

        if not candidate_labels:
            candidate_labels = ["Software Engineer", "Data Analyst"]

        classifier = get_zero_shot()
        if classifier and self.text:
            # Use HuggingFace zero-shot semantic classification to deeply understand the text
            # We take the first 1000 chars to avoid memory/token limits
            result = classifier(self.text[:1000], candidate_labels)
            top_roles = result["labels"][:5]
            if top_roles:
                return top_roles

        # Classical overlap fallback if HuggingFace isn't loaded
        skill_lower = {s.lower() for s in skills}
        scores = Counter()
        for role in roles:
            role_skills = [s.skill_name.lower() for s in role.skills.all()]
            overlap = len(skill_lower.intersection(set(role_skills)))
            scores[role.title] = overlap

        top_roles = [role for role, score in scores.most_common(5) if score > 0]

        if not top_roles and candidate_labels:
            return candidate_labels[:3]

        return top_roles

    def find_gaps_and_courses(self, top_role: str, current_skills: list[str]):
        try:
            role_obj = CareerRole.objects.get(title=top_role)
            required = {s.skill_name.lower() for s in role_obj.skills.all()}
        except CareerRole.DoesNotExist:
            db_skills = RoleSkill.objects.values_list(
                "skill_name", flat=True
            ).distinct()[:10]
            generic_skills = (
                [s for s in db_skills]
                if db_skills
                else ["Communication", "Problem Solving"]
            )

            current = {s.lower() for s in current_skills}
            missing = [s for s in generic_skills if s.lower() not in current]
            return missing[:5], [
                f"Online Platform: {m} Masterclass" for m in missing[:5]
            ]

        current = {s.lower() for s in current_skills}
        missing = list(required - current)[:5]

        gaps = [s.title() for s in missing]
        courses = []
        for m in missing:
            course = CourseRecommendation.objects.filter(skill_name__iexact=m).first()
            if course:
                courses.append(f"{course.provider}: {course.course_title}")

        return gaps, courses

    def generate_interview_qs(self, top_role: str) -> list[str]:
        try:
            role_obj = CareerRole.objects.get(title=top_role)
            questions = [q.question_text for q in role_obj.questions.all()][:5]
            if not questions:
                raise CareerRole.DoesNotExist
            return questions
        except CareerRole.DoesNotExist:
            db_qs = InterviewQuestion.objects.order_by("?")[:5]
            if db_qs:
                return [q.question_text for q in db_qs]
            return [
                f"Can you describe your experience with technologies related to {top_role}?",
                "What is the most challenging project you've worked on recently?",
                "How do you approach solving complex technical problems?",
                "Describe a time you had to work with a difficult team member.",
                "How do you stay updated with the latest industry trends?",
            ]

    def get_improvements(self, gaps: list[str]) -> list[str]:
        improvements = []
        for gap in gaps:
            improvements.append(
                f"Add projects explicitly demonstrating your skills in {gap}."
            )
        return improvements

    def _extract_section(self, section_name: str) -> list[str]:
        lines = [line.strip() for line in self.text.split("\n") if line.strip()]
        in_section = False
        content = []
        for line in lines:
            lower_line = line.lower()
            # If we see a short line that matches the section name
            if section_name in lower_line and len(line) < 30:
                in_section = True
                continue
            # If we see another heading, stop
            elif (
                in_section
                and len(line) < 30
                and any(
                    kw in lower_line
                    for kw in [
                        "experience",
                        "education",
                        "skills",
                        "projects",
                        "summary",
                        "profile",
                        "objective",
                    ]
                )
                and section_name not in lower_line
            ):
                break

            if in_section:
                content.append(line)
        return content

    def extract_summary(self) -> str:
        summary_lines = (
            self._extract_section("summary")
            or self._extract_section("profile")
            or self._extract_section("objective")
        )
        return (
            " ".join(summary_lines)
            if summary_lines
            else "No professional summary detected."
        )

    def extract_projects(self) -> list[str]:
        return self._extract_section("project")

    def extract_experience(self) -> list[str]:
        return self._extract_section("experience")

    def extract_academic_records(self) -> list[dict]:
        edu_lines = self._extract_section("education") or self._extract_section(
            "academic"
        )
        if not edu_lines:
            return []
        return [
            {
                "degree": " ".join(edu_lines)[:150],
                "institution": "Offline Extracted",
                "graduation_year": 2024,
                "cgpa": 0.0,
            }
        ]
