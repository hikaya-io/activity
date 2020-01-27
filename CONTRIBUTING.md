# Contributing to Hikaya

Thanks for checking out Activity. Activity is an open source project currently maintained by Hikaya.

## Table of Contents

1. [Ground rules & expectations](#ground-rules--expectations)
2. [How to contribute](#how-to-contribute)
3. [Contribution review process](#contribution-review-process)
4. [Community](#community)

## Ground rules & expectations

Before we get started, here are a few things we expect from you (and that you should expect from others):

- Be kind and thoughtful in your conversations around this project. We all come from different backgrounds and projects, which means we likely have different perspectives on "how open source is done." Try to listen to others rather than convince them that your way is correct.
- Activity Community Versions are released with a [Contributor Code of Conduct](./CODE_OF_CONDUCT.md). By participating in this project, you agree to abide by its terms.
- If you open a pull request, please ensure that your contribution passes all tests. If there are test failures, you will need to address them before we can merge your contribution.
- When adding content, please consider if is widely valuable. Please don't add references or links to things you or your employer have created as others will do so if they appreciate it.

## How to contribute

If you'd like to contribute, start by searching through the [issues](https://github.com/hikaya/Activity-CE/issues) and [pull requests](https://github.com/hikaya/Activity-CE/pulls) to see whether someone else has raised a similar idea or question. If you see none, feel free to reach out to us at info@hikaya.io to join our working board.

If you don't see your idea listed, and you think it fits into the goals of this guide, do one of the following:

- **If your contribution is minor,** such as a typo fix, **or self-contained,** such as writing a translation, open a pull request.
- **If your contribution is major,** such as a new functionality, start by opening an issue first. That way, other people can weigh in on the discussion before you do any work.

## Our development process

**Source control:** Git

**Branches:**

- `Develop` (or `Dev`) - All bug fixes and enhancements
- Feature branches (i.e. `ACT-001`) - All feature branches must be named like: ACT-001 (where ACT-001 is the issue number on Jira)
- `Master` - Clean code in production environment

**Hot-fixes & bug-fixes**

- All hot-fixes will be done off master branch
- All hotfix branches must be named like: `ACT-001` (where ACT-001 is the issue number on Jira)
- All bug-fixes will done off dev branch
- All bugfix branches must be named like: `ACT-001` (where ACT-001 is the issue number on Jira)

**Commits (Smart Commits)**

- For us to be able to track and link our issues on Jira from Github, we use smart commits. Below is an example of smart commit:
  - ACT-001:- Update Activity UI based on styling guide
  - ACT-001:- is the issue number on Jira
    - “Update Activity UI based on styling guide” Is the commit body. This should be as descriptive as possible.

**Pull Requests**

- All developers MUST submit Pull Requests for any change made on any of the Hikaya Repositories
- The PR must be reviewed by at least one developer other than the author
- PR Checkpoints:
  - Application is not broken
  - All set checks passes (We will set the checks for each individual project)
  - The bug/feature/enhancement in question is fully addressed
- PRs must follow the predefined template. In the PR body, the following questions and/or points must be addressed (This is templated when creating a new PR):
  - Descriptive Title
  - What is the purpose of the PR?
  - Approach used to address the issue
  - Any prerequisites before/after merging?
  - Review requests
  - Affected Issue(s)
- Deployment
  - We will set up a CI/CD process for deployment to all our environments
  - Any developer should be able to deploy their changes to `develop` environment

## Contribution review process

This repo is currently maintained by Hikaya, who have commit access. They will likely review your contribution. If you haven't heard from anyone in 10 days, feel free to bump the thread or @-mention a maintainer to review your contribution.

## Community

Discussions about Activity take place in the Issues sections for each repo, as well as http://hikaya-io.slack.com. Anybody is welcome to join these conversations. Send us message at info@hikaya.io for an invite to Slack.

Wherever possible, do not take these conversations to private channels, including contacting the maintainers directly. Keeping communication public means everybody can benefit and learn from the conversation.
