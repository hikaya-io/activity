# Contributing to Hikaya
 
Thanks for checking out Activity. Activity is an open source project currently maintained by Hikaya.
 
## Table of Contents
 
- [Contributing to Hikaya](#contributing-to-hikaya)
  - [Table of Contents](#table-of-contents)
  - [Ground rules & expectations](#ground-rules--expectations)
  - [How to contribute](#how-to-contribute)
  - [Our development process](#our-development-process)
  - [Contribution review process](#contribution-review-process)
  - [Coding Conventions](#coding-conventions)
    - [Github Labels](#github-labels)
    - [Naming conventions](#naming-conventions)
    - [Code standards](#code-standards)
    - [CI/CD](#cicd)
  - [Community](#community)
 
## Ground rules & expectations
 
Before we get started, here are a few things we expect from you (and that you should expect from others):
 
- Be kind and thoughtful in your conversations around this project. We all come from different backgrounds and projects, which means we likely have different perspectives on "how open source is done." Try to listen to others rather than convince them that your way is correct.
- Activity Community Versions are released with a [Contributor Code of Conduct](./CODE_OF_CONDUCT.md). By participating in this project, you agree to abide by its terms.
- If you open a pull request, please ensure that your contribution passes all tests. If there are test failures, you will need to address them before we can merge your contribution.
- When adding content, please consider if it is widely valuable. Please don't add references or links to things you or your employer have created as others will do so if they appreciate it.
 
## How to contribute
  - Look through the [issues](https://github.com/hikaya/activity/issues). 
 
If you'd like to contribute, start by searching through the [issues](https://github.com/hikaya/activity/issues) and [pull requests](https://github.com/hikaya/activity/pulls) to see whether someone else has raised a similar idea or question. If you see none, feel free to reach out to us on [Spectrum]("https://spectrum.chat/hikaya)

  - If you find an issue you would like to work on, feel free to assign it to yourself.
  - If you don't find one you would like to work on, create an issue, assign a label and @mention one of the maintainers to let them know about the issue.
 
## Our development process
 
**Source control:** Git
 
**Branches:**
 
We have 3 main branches in our repo:
- `Dev` - All bug fixes and enhancements
- Feature branches (i.e. `ACT-001`) - All feature branches must be named like: ACT-001 (where ACT-001 is the issue number on Jira)
- `Staging` - This is our QA testing environment
- `Master` - Clean code in production environment
 
**Hot-fixes & bug-fixes**
 
- All pull requests should be based off of the `Dev` branch.
- All branch names should follow the issue number such as: `ACT-001`. This should be the Github issue number.
 
**Commits (Smart Commits)**
 
- For us to be able to track and link our issues on Github, we use smart commits (This is for issues tracked in Jira). Below is an example of smart commit:
  - ACT-001:- Update Activity UI based on styling guide
  - ACT-001:- is the issue number on Jira
    - “Update Activity UI based on styling guide” Is the commit body. This should be as descriptive as possible.
 
**Pull Requests**
 
- All developers MUST submit Pull Requests for any change made on any of the Hikaya Repositories.
- The PR must be reviewed by at least **two developers** other than the author.
- PR Checkpoints:
  - All set checks passes (We will set the checks for each individual project).
  - The bug/feature/enhancement in question is fully addressed
  - PRs must follow the predefined template. In the PR body, the following questions should be addressed (This is predefined when creating a new PR):
  	- Descriptive Title
 	- What is the purpose of the PR?
  	- Approach used to address the issue
  	- Any prerequisites before/after merging?
  	- Review requests
  	- Affected Issue(s)
  	- Check that the application still functions as before
- Deployment
  - We will set up a CI/CD process for deployment to all our environments
  - Any developer is allowed to deploy their changes to `dev` environment. To request access, contact one of the maintainers.
 
## Contribution review process
 
This repo is currently maintained by Hikaya, who have commit access. They will likely review your contribution. If you haven't heard from anyone in 5 days, feel free to bump the thread or @-mention a maintainer to review your contribution.
 
## Coding Conventions
 
### Github Labels
  - ```Good first issue``` - Good for newcomers
  - ```bug``` - Something isn't working
  - ```defect``` - Something isn't working right
  - ```enhancement``` - New feature 
  - ```dependencies``` - Updates dependecies
  - ```duplicate``` - Issue or pullrequest exists
  - ```help wanted``` - Extra attention is required
  - ```question``` - More information is needed
  - ```level 0``` - Insignificant task (minimal effort and time needed)
  - ```level 1``` - Simple issues requiring minimal effort
  - ```level 2``` - Not so complex, requiring a relatively goot amount of effort and time to fix
  - ```level 3``` - Complex task
  - ```level 4``` - Very complext task
 
 
### Naming conventions
  - All folder names should only contain lowercase characters.
  - All file names should have only lowercase characters and spaces should be substituted with underscores.
 
### Code standards
 
  **Django views**
    - Views should be implemented using class-based views instead of function-based views.
 
  **Unit tests**
    - We encourage all developers to build unit tests when adding new functionality.
 
  **Linting**
    - Code submitted in a PR should be free of linting issues and adhere to `PEP8` standards.
    - The project uses `Flake8` for python code linting.
 
### CI/CD
  - We are currently using Github Actions for simple build checks.
  - In the future, we will introduce more rigorous checks including unit tests, integration tests, end-to-end tests, and automatic deployments to `dev`.
 
## Community
 
Discussions about Activity take place in the Issues sections for each repo, as well as on [Spectrum](https://spectrum.chat/hikaya). Anybody is welcome to join these conversations.
 
Thanks for contributing!
