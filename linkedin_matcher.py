import logging
import re
from linkedin_jobs_scraper import LinkedinScraper
from linkedin_jobs_scraper.events import Events, EventData
from linkedin_jobs_scraper.query import Query, QueryOptions, QueryFilters
from linkedin_jobs_scraper.filters import RelevanceFilters, TimeFilters, TypeFilters, ExperienceLevelFilters, \
    OnSiteOrRemoteFilters, IndustryFilters

from openai import OpenAI
from job_cache import init_cache, job_seen, mark_job_seen

# Load CV once
with open("cv.txt", "r", encoding="utf-8") as f:
    cv_text = f.read()

# OpenAI client
client = OpenAI()
init_cache()  # Initialize DB on startup

# Store matches
high_score_matches = []


def extract_job_id(link: str) -> str | None:
    if '/jobs/collections/' in link:
        return None  # Skip injected/recommended jobs
    match = re.search(r'/jobs/view/(\d+)', link)
    return match.group(1) if match else None


def extract_score(text: str) -> float:
    match = re.search(r'Final Score:\s*(\d+(?:\.\d+)?)/10', text)
    return float(match.group(1)) if match else 0.0


def match_job_to_cv(job_description: str) -> tuple[str, float]:
    job_description = job_description.strip().replace(
        '\r\n', '\n').replace('\n\n', '\n')
    response = client.chat.completions.create(
        model="gpt-4.1",
        messages=[
            {"role": "system", "content": "You are a technical recruiter comparing a candidate's CV with a job description. Be precise and concise."},
            {"role": "user", "content": f"""Here is the job description:

{job_description}

And here is the CV:

{cv_text}

How well does this CV match the job description? Give a bullet-point analysis, including strengths, gaps, and an overall match score from 1 to 10.

Scoring notes:
- Add 1 point if the job description is primarily written in English.
- Subtract 1 point if the role is heavily focused on software development or programming (rather than DevOps, SRE, Infrastructure, or platform engineering).

At the end, output only this line on a new line:

Final Score: X/10
"""}
        ],
        temperature=0.3
    )
    content = response.choices[0].message.content
    score = extract_score(content)
    return content, score


def on_data(data: EventData):
    job_id = extract_job_id(data.link)
    if not job_id:
        print("[WARNING] Could not extract job ID from:", data.link)
        return

    if job_seen(job_id):
        print(f"[SKIPPED] Job already seen: {data.title} | {data.company}")
        return

    print('[ON_DATA]', data.title, '|', data.company)
    print('URL:', data.link)
    if data.description:
        try:
            result, score = match_job_to_cv(data.description)
            print('\nAI Match Result:')
            print(result)
            if score >= 7:
                high_score_matches.append(
                    (data.title, data.company, data.link, score))
        except Exception as e:
            print(f"[ERROR during AI match]: {e}")
    else:
        print("[WARNING]: No job description provided.")

    mark_job_seen(job_id)
    print('-' * 100)


def on_error(error):
    print('[ON_ERROR]', error)


def on_end():
    print('[ON_END]')
    if high_score_matches:
        print('\n Jobs You Should Apply For:')
        for title, company, link, score in high_score_matches:
            print(f"- {title} at {company} | Score: {score}/10")
            print(f"  {link}")
        titles = ', '.join([title for title, _, _, _ in high_score_matches])
    else:
        print("\n No strong matches (score ≥ 7) found this round.")


# Setup logging and scraper
logging.basicConfig(level=logging.INFO)

scraper = LinkedinScraper(
    chrome_options=None,
    max_workers=1,
    slow_mo=1,
)

scraper.on(Events.DATA, on_data)
scraper.on(Events.ERROR, on_error)
scraper.on(Events.END, on_end)

queries = [
    Query(
        query='DevOps',
        options=QueryOptions(
            locations=['France'],
            limit=60,
            filters=QueryFilters(
                relevance=RelevanceFilters.RECENT,
                time=TimeFilters.DAY,
                type=[TypeFilters.FULL_TIME, TypeFilters.CONTRACT],
                experience=[
                    ExperienceLevelFilters.MID_SENIOR,
                    ExperienceLevelFilters.DIRECTOR,
                    ExperienceLevelFilters.EXECUTIVE
                ],
                on_site_or_remote=[
                    OnSiteOrRemoteFilters.REMOTE,
                    OnSiteOrRemoteFilters.HYBRID
                ],
                industry=[
                    IndustryFilters.IT_SERVICES,
                    IndustryFilters.TECHNOLOGY_INTERNET,
                    IndustryFilters.INFORMATION_SERVICES,
                    IndustryFilters.BANKING,
                    IndustryFilters.SOFTWARE_DEVELOPMENT,
                    IndustryFilters.FINANCIAL_SERVICES
                ],
            )
        )
    ),
]

scraper.run(queries)
