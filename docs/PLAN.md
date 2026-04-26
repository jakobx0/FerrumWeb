# FerrumWeb Plan

FerrumWeb should become a web discovery, classification, and visualization project. The goal is not to build only a crawler or only a visualizer, but a pipeline that collects pages, understands them, stores them cleanly, and makes the results explorable.

The rough flow should be:

`crawl -> extract -> store -> detect -> visualize -> label -> improve`

## Direction

The crawler should discover pages and relationships between pages. On top of that, the project should classify pages into user-defined categories such as `job_offer`, `career_page`, `auth_page`, or `admin_page`. Later, those classifications can be improved with labeled data and ML.

This means FerrumWeb should mainly focus on:

- reliable crawling
- reusable data storage
- dynamic detectors
- useful visualization
- later ML support

## Core Parts

The crawler should start from one or more seed URLs, resolve relative links, normalize URLs, respect scope limits, and optionally respect `robots.txt`. It should use a queue-based crawl process instead of deep recursion.

The storage layer should keep pages, edges, crawl sessions, extracted features, findings, and labels separate. A page should be stored once, while relationships between pages should be stored separately.

The feature extraction layer should pull out the signals detectors need. That includes title, headings, visible text, links, forms, metadata, and structured data.

The detection layer should be config-driven. Instead of hardcoding categories into Rust, detectors should be defined in `YAML` or `JSON` and produce a score, a reason, and evidence.

The visualization layer should show the crawl graph, color pages by category, and provide a findings view with filtering and confidence values.

## ML Direction

ML should improve the detector system, not replace the crawler.

The best order is:

- build rule-based detectors first
- store findings and extracted features
- manually label pages
- train a simple model on labeled data
- use the model to improve ranking or classification

Rust should handle crawling, storage, extraction, and rule execution. Python is the better fit for training and evaluation.

## Rough Data Model

FerrumWeb should move toward a small normalized schema.

Important entities:

- `crawl_session`
- `page`
- `edge`
- `fetch_result`
- `page_feature`
- `finding`
- `label`
- `robots_cache`

The most important rule is simple: store pages once, store links between pages separately.

## Roadmap

- fix the crawl core by replacing recursion with a frontier queue, resolving relative URLs correctly, normalizing URLs, and separating page storage from edge storage
- add crawl policy with scope limits, a `robots.txt` toggle, and per-host robots caching
- add feature extraction so fetched pages become reusable structured data instead of just raw HTML
- add dynamic detectors with a detector config format, a rule engine, and stored findings with score and evidence
- improve visualization so the graph shows categories, findings, and confidence in a way that supports review
- add labels and ML once the crawl data and detector output are stable

## First Good Version

The first strong version of FerrumWeb should be able to:

- crawl a site correctly
- store unique pages and separate edges
- respect or ignore `robots.txt`
- run at least one config-based detector
- visualize categories on the graph
- export data for labeling or ML

## First Detector

`job_offer` is the best first detector. It is easier to define, easier to label, and easier to visualize than broader or security-oriented categories.

## Immediate Next Steps

- redesign the database schema
- redesign the crawler as a queue-based system
- define the extracted feature format
- define the detector config format
- implement one detector end to end
