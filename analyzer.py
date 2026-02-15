from __future__ import annotations

import re
from dataclasses import dataclass

CTA_KEYWORDS = {
    "comment",
    "share",
    "follow",
    "subscribe",
    "save",
    "tag",
    "dm",
    "click",
    "link in bio",
}


@dataclass
class AnalysisResult:
    summary: str
    score: int
    suggestions: list[str]
    metrics: dict[str, int]


def analyze_social_post(text: str) -> dict:
    cleaned = " ".join((text or "").split())
    if not cleaned:
        return AnalysisResult(
            summary="No text found to analyze.",
            score=0,
            suggestions=["Upload a clearer file or higher-resolution scan."],
            metrics={"word_count": 0, "hashtag_count": 0, "mention_count": 0},
        ).__dict__

    words = re.findall(r"\b\w+\b", cleaned)
    hashtags = re.findall(r"#[\w_]+", cleaned)
    mentions = re.findall(r"@[\w_.]+", cleaned)
    lowered = cleaned.lower()

    has_cta = any(keyword in lowered for keyword in CTA_KEYWORDS)

    score = 50
    suggestions: list[str] = []

    word_count = len(words)
    hashtag_count = len(hashtags)

    if 25 <= word_count <= 120:
        score += 15
    elif word_count < 25:
        score -= 10
        suggestions.append("Add more context. Very short posts often get lower engagement.")
    else:
        score -= 8
        suggestions.append("Tighten the copy. Long posts can lose reader attention.")

    if 1 <= hashtag_count <= 5:
        score += 10
    elif hashtag_count == 0:
        score -= 6
        suggestions.append("Add 1-3 relevant hashtags to improve discoverability.")
    else:
        score -= 5
        suggestions.append("Reduce hashtags; too many may look spammy.")

    if has_cta:
        score += 12
    else:
        score -= 7
        suggestions.append("Include a call-to-action (e.g., ask users to comment or share).")

    if len(mentions) > 0:
        score += 5
    else:
        suggestions.append("Consider tagging a partner/brand for added reach where relevant.")

    if "?" not in cleaned:
        suggestions.append("Add a question to invite replies and boost comments.")

    score = max(0, min(100, score))

    if score >= 80:
        summary = "Strong engagement potential."
    elif score >= 60:
        summary = "Good baseline with room for improvement."
    else:
        summary = "Needs optimization for better engagement."

    result = AnalysisResult(
        summary=summary,
        score=score,
        suggestions=suggestions,
        metrics={
            "word_count": word_count,
            "hashtag_count": hashtag_count,
            "mention_count": len(mentions),
        },
    )

    return result.__dict__