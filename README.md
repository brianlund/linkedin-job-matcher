# AI CV Match (GPT-4)

A Python tool that scrapes LinkedIn job listings using [py-linkedin-jobs-scraper](https://github.com/spinlud/py-linkedin-jobs-scraper) and uses GPT-4 to score each job against your CV. At the end of a run, it highlights high-scoring matches.
---

## Features

- Scrapes LinkedIn with configurable filters (location, seniority, remote, industry, etc.). See [py-linkedin-jobs-scraper](https://github.com/spinlud/py-linkedin-jobs-scraper) for configuration and filtering
- Uses GPT-4 to analyze how well a job matches your CV.
- Skips jobs you've already seen using a lightweight SQLite cache.
- Notifies you of good matches

---

## Requirements

- Python 3.10+
- Chrome + Chrome Webdriver (scraper reqs)
- [OpenAI API key](https://platform.openai.com/account/api-keys) as ENV OPENAI_API_KEY
- A valid LinkedIn session cookie (`li_at`) `py-linkedin-jobs-scraper' has details on how to obtain it, as ENV LI_AT_COOKIE
- [py-linkedin-jobs-scraper](https://github.com/spinlud/py-linkedin-jobs-scraper)

---

## Usage

- Provide your CV as cv.txt in the root folder
- export OPENAI_API_KEY="your-key-here" ; export LI_AT_COOKIE="your-linkedin-session-cookie-here"


## Output

Example of output:

```
Jobs You Should Apply For (Score => 7):
- DevOps Cloud Confirmé (F/H) with verification at VISEO | Score: 8.0/10
  https://www.linkedin.com/jobs/view/4217413510/
- Intégrateur DevOps – Observabilité & Monitoring H/F at STEP UP | Score: 8.0/10
  https://www.linkedin.com/jobs/view/4231599509/
- Devops / Cloud OPS Clermont-Ferrand H/F (IT) / Freelance at Free-Work | Score: 7.0/10
  https://www.linkedin.com/jobs/view/4229471673/
```

## Notes

The linkedIn search can be a bit flakey, run it again if no jobs are returned and if the problem persists, check your queries and filters for py-linkedin-jobs-scraper

## License
MIT

## Acknowledgements
[py-linkedin-jobs-scraper](https://github.com/spinlud/py-linkedin-jobs-scraper)
