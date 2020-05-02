_UPDATED: 20200502_

# Contributing to Hikaya
 
Thanks for checking out **Activity**. Activity is an open source project currently maintained by the team at [Hikaya](https://hikaya.io/team).

## Table of Contents
 
- [Contributing to Hikaya](#contributing-to-hikaya)
  - [Table of Contents](#table-of-contents)
  - [Ground rules and expectations](#ground-rules-and-expectations)
  - [How to contribute](#how-to-contribute)
    - [Contribution review process](#contribution-review-process)
    - [For long-term contributors](#for-long-term-contributors)
    - [Tips on how to best engage and contribute](#tips-on-how-to-best-engage-and-contribute)
    - [Role of Maintainers](#role-of-maintainers)
    - [Community](#community)
  - [Development Process](#development-process)
    - [Roadmap](#roadmap)
    - [How we work](#how-we-work)
    - [Planning](#planning)
      - [Bug report](#bug-report)
      - [Feature request](#feature-request)
      - [Definition of done](#definition-of-done)
  - [Navigating our repos](#navigating-our-repos)
    - [Labels](#labels)
    - [Milestones](#milestones)
    - [Task board](#task-board)
      - [Triage](#triage)
      - [Hardening sprint](#hardening-sprint)
    - [QA testing](#qa-testing)
  - [How we manage our code](#how-we-manage-our-code)
    - [Commits](#commits)
    - [Pull Requests](#pull-requests)
    - [Deployments](#deployments)
    - [Coding Conventions](#coding-conventions)
      - [Naming conventions](#naming-conventions)
      - [Code standards](#code-standards)


## Ground rules and expectations
 
Before we get started, here are a few things we expect from you (and that you should expect from others):
 
- Be kind and thoughtful in your conversations around this project. We all come from different backgrounds and projects, which means we likely have different perspectives on "how open source is done." Try to listen to others rather than convince them that your way is correct.
- Activity Community Versions are released with a [Contributor Code of Conduct](./CODE_OF_CONDUCT.md). By participating in this project, you agree to abide by its terms.
- If you open a pull request, please ensure that your contribution passes all tests. If there are test failures, you will need to address them before we can merge your contribution.
- When adding content, please consider if it is widely valuable. Please don't add references or links to things you or your employer have created as others will do so if they appreciate it.

## How to contribute
All contributors are welcome to submit issues and make pull requests to the repository.

- Look through the [issues](https://github.com/hikaya-io/activity/issues?q=is%3Aopen+is%3Aissue+no%3Aassignee+-label%3AEpic).
 
If you'd like to contribute, start by searching through the [issues](https://github.com/hikaya/activity/issues) and [pull requests](https://github.com/hikaya/activity/pulls) to see whether someone else has raised a similar idea or question. If you see none, feel free create an issue and ask for guidance on where to start.

- If you find an issue you would like to work on, feel free to assign it to yourself.
- If you don't find one you would like to work on, create an issue, assign a label and @mention one of the maintainers to let them know about the issue.

### Contribution review process
 
This repo is currently maintained by Hikaya, who have commit access. They will likely review your contribution. If you haven't heard from anyone in 5 days, feel free to bump the thread or @-mention a maintainer to review your contribution.

### For long-term contributors

Long standing contributors will be given `write` access to the repository. In addition, we have slots for contributors to be given `maintainer` status which allows contributors to administer the repository, support the onboarding of new contributors, and influence the product roadmap.

Our current maintainers are: Peter Odeny ([@odenypeter](https://github.com/odenypeter)) and Isaac Kimaiyo ([@Kimaiyo077](https://github.com/kimaiyo077)).

### Tips on how to best engage and contribute

1. **Determine how many hours you can commit to each week.** Think about how many hours you can commit to each week. Currently many of our contributors spend around ~20-25 hours a week but there is no minimum, only that you set your own hours.
2. **Come up with your own weekly schedule and propose it to the team.** If you have certain days and times you are tentatively available you can put together a schedule of what a typical week will look like so others can try and sync with you or know when to reach out on slack. These  are just tentative and used by other contributors to coordinate calls between each other.
3. **Try to make at least one of the sprint calls each week (Monday and Saturday 7 PM EAT).** If you can’t make a call, kindly write on the #sprint-planning slack channel or message me before hand so we can know if you are able to join or not. We just ask for communication courtesy but understand contributors won’t be able to make each call.
4. **Ask for help when you need it** Our philosophy is to let contributors work on anything they think could add value to our apps. The core team at Hikaya will try to make themselves available to support any new onboarding or even have paired programming sessions on an issue to help you get started. We kindly ask all contributors to not be shy and ask for help when you need it.
5. **Be open and communicate** If life has gotten busy or priorities have changed and you can no longer contribute, no worries, we completely understand! All we ask is for you to communicate and let us know upfront so we can plan accordingly. You're always welcome to pause and contribute another time.

### Role of Maintainers

- Set priorities for each sprint in coordination with the product and technical leads.
- Maintain and ensure consistent and proper use of the sprint board.
- Be a reviewer for many tasks. Clear communication will be done at the beginning of the sprint around which tasks will be reviewed by whom.
- “Coach” other members as they work on their tasks.

### Community
 
Discussions about Activity take place in the `Issues` sections for each repo, as well as on [Spectrum](https://spectrum.chat/hikaya). Anybody is welcome to join these conversations.
 
Thanks for contributing!

---

# Development Process

## Roadmap

The team has a 6-12 month high-level product roadmaps ([See Activity Roadmap](https://team.hikaya.io/start/activity-roadmap.html)) which defines epics and feature sets to be addressed during this period.

## How we work

We will work in two-week **Sprints** on the items on the roadmap. At the end of each sprint, we want to have a stable release of **Activity** that can be shipped to our users. The work planned during a sprint is captured in the Task board. The feature sets of each sprint are highlighted in a published [**Release**](https://github.com/hikaya-io/activity/releases) in Github.

**A typical month**

> **Week 1**: Reduce debt introduced in the previous iteration, address critical issues uncovered in the previous iteration, and plan the next iteration.

> **Week 2**: Work according to the milestone and minor release to `production`.

> **Week 3+**: Work according to the milestone and
monitoring the minor release and fix critical issues.

> **Final Week**: See `Hardening Sprint`. The team improves test coverage by building tests and cleaning up unused code and templates. Deploy to `production` and showcase new features.

We follow a typical checklist before we ship new features:<br>
✅Pull Requests are reviewed and merged to `dev` branch.<br>
✅Issue is deployed to `staging` environment and passes user acceptance testing (UAT).<br>
✅Manually execute the Smoke Test on all supported platforms.<br>
✅Release notes updated.<br>
✅Deploy to `production`.<br>

## Planning

Before each Milestone, we will prioritize features to implement and bugs to fix in the upcoming iteration. `Bugs` and `Defects` are assigned to a sprint for the iteration and include steps to reproduce and `current and expected behaviors`. For new features, we create `Tasks` and include `Acceptance Criteria`.

We use the following definitions to track our issues:
* **Bug**: An issue that stop the user from doing what they intended.
* **Defect**: An issue that does not do what it was intended to do.
* **Task**: An issue that is an enhancement or new feature.

### Bug Report

> **Current behavior**<br>
_A clear and concise description of what the bug is._

> **Expected behavior**<br>
_A clear and concise description of what you expected to happen._

> **To Reproduce:**
```
Steps to reproduce the behavior:
1. Go to '...'
2. Click on '....'
3. Scroll down to '....'
4. See error
```

>**Screenshots**<br>
_If applicable, add screenshots to help explain your problem._

### Feature Request

> **Is your feature request related to a problem? Please describe.**<br>
_A clear and concise description of what the problem is._

> **Acceptance Criteria**<br>
_A clear and concise description of how to ensure the feature request is met._

```
GIVEN I am a logged in user

AND I navigate to the main page...

AND I click on the button.

THEN I expect this to happen..
```
> **Additional context**<br>
_Add any other context or screenshots about the feature requests._

### Definition of Done
Each issue card will have an **Acceptance Criteria** that defines the definition of done for every task that is worked on.

---

## Navigating our repos

### Labels

We use **Github Labels* to describe the task card including its priority and complexity. Here is a list that we try to consistently use across all our applications:

|Label|Description|
|--|--|
|`Good first issue`|Good for newcomers|
|`bug`|Something isn't working|
|`defect`| Something isn't working right|
|`enhancement`|New feature|
|`dependencies`|Updates dependencies|
|`duplicate`|Issue or pull request exists|
|`help wanted`|Extra attention is required|
|`requires research`|Further information is required|
|`priority`|High priority issue|
|`design needed`|Requires a wireframe|
|`tests`|For unit and integration tests|
|`0`|Insignificant task (minimal effort and time needed)|
|`1`|Simple issues requiring minimal effort|
|`2`|Not so complex, requiring a relatively good amount of effort and time to fix|
|`5`|Complex task|
|`8`|Very complex task|

> **Story point estimation**<br> 
> Story points are used to estimate the effort needed for each task. We try to avoid using time estimates and a more useful measurement for team capacity is the effort needed and then complexity of a task.

| Story Point | Complexity reference  |
|--|--|
| 1 | Changing a label |
| 2 | Making a model change |
| 3 | Implementing CRUD on the UI |
| 5 | Implementing a new model|
| 8 | Introducing complex logic|
| 13| Research task, building a proof of concept |
| 21| Should be used sparingly|

## Milestones

We work toward a **Sprint** with the goal to release to `production` every two weeks. We use **Github Milestones** to track what issues contributors work on during a specific Sprint. Each milestone will have a start and end date and the product team will help to groom the issues and tag them to a specific sprint number before the sprint starts.

Each week we have two calls as a team to discuss our priorities and reflect:
* **Sprint Planning:** every Monday 7 PM EAT
* **Sprint Review:** every Saturday 7 PM EAT

> Join calls using `Google Meet` and follow the `#sprint-planning channel` on slack.

## Task Board
We use **Github Projects** to manage our current sprints with automated workflows. Each repo will have its own task board to manage issues and will consist of the following columns:
- `To do`
- `In progress`
- `Pull request`
- `Dev testing`
- `Staging`
- `Done`

Before every sprint, we archived all issues in the `Done` columns and add issue cards with the current sprint milestone tagged to them. During our sprint calls, the team will groom, discuss, and assign cards to contributors to work on.

> **Note:**
> * At the beginning of every milestone, we include all items in the `To do` stage and move them over as we go. 
> * At the end of a milestone, any issues in `To do` or `In Progress` need to be moved over to the next sprint (if still relevant) or turned into new issues.

### Triage

Bugs and features will be assigned a sprint, and within a sprint, they will be assigned a priority. The priority dictates the order in which issues should be addressed. An important bug (something that we think is critical for the milestone) is to be addressed before the other bugs.

### Hardening Sprint

The final week of the month is what we call the "Hardening Sprint". During this week we will fix the critical bugs and focus the entire week on improving test coverage by building unit and integration tests for any new features. 

Note:
> Currently since we have been refactoring the app, the upcoming hardening sprints will be focused on adding tests to existing features. Our plan is to go app by app and build test

During this period we make a build available on the insiders channel. We will monitor incoming issues from this release, fix any critical bugs that arise, and then produce a final stable release for the monthly iteration.

## QA testing
We perform QA testing when features are merged from `develop` to `staging`. We use automated end-to-end testing to provide a strong foundation for functional testing.

---

# How we manage our code

**Source control:** Git

**Source code:** All our repositories are stored on [GitHub](https://github.com/hikaya-io).

**Branches:**

We use 3 main branches in all our repositories :

`Dev` (or `Develop`) - All bug fixes, defects, and tasks.<br>
`Feature branches` (i.e. ACT-001) - All feature branches must be named like: ACT-001 (where ACT-001 is the issue number on GitHub).<br>
`Staging` - This is our QA testing environment<br>
`Master` - Clean code in production environment<br>

> **Note:**
> * All pull requests should be based off of the `develop` branch.
> * All branch names should follow the issue number such as: ACT-001. The numbering should follow the auto-generated GitHub issue number.

## Commits

We use Github to track **Issues** and **Pull Requests** for all our work. When making commits, please ensure that you have create a separate branch off of the main `develop` branch before you begin making changes to the source code. Feel free to make commits as often as possible to your branch. If the issue you are working on has been open for a few days, consider pulling in the latest changes to keep in up to date with the main `develop` branch before you create a Pull Request. This will help you avoid merge conflicts when raising your Pull Request.

### Commit message format
To ensure commit messages are readable when going through project history, we use a common commit message format. The message format by [Angular](https://github.com/angular/angular.js/blob/master/DEVELOPERS.md#-git-commit-guidelines) is very comprehensive and we find it useful to follow.

Each commit message consists of a header, a body and a footer. The header is mandatory with the body and the footer as optional given the size of the commit. The header has a special format that includes a type, a scope, and a subject, where the scope of the header is optional.

```
<type>(<scope>): <subject>
<BLANK LINE>
<body>
<BLANK LINE>
<footer>
```

Please refer to the [Angular guidelines](https://github.com/angular/angular.js/blob/master/DEVELOPERS.md#-git-commit-guidelines) for more details on the format.

## Pull Requests

Once you have pushed code and your branch to Github, you can open a Pull Request. There are two types of Pull Requests: *Draft* and *Ready for review*. Feel free to create a draft Pull Request for larger features that require additional input from other contributors or is a research/proof of concept task.

Here are some guidelines for making Pull Requests:
- All developers MUST submit Pull Requests for any change made on any of the Hikaya Repositories.
- The PR must be reviewed by at least **two developers** other than the author.
- PR Checkpoints:
  - All set checks passes (We will set the checks for each individual project).
  - The bug/feature/enhancement in question is fully addressed
  - PRs must follow the predefined template. In the PR body, the following questions should be addressed (This is predefined when creating a new PR):
  	- Descriptive Title: Add the issue number followed by a brief description of the ticket e.g., `ACT-001: Adds project status`
  - What is the purpose of the PR?
  	- Approach used to address the issue
  	- Any prerequisites before/after merging?
  	- Review requests
  	- Affected Issue(s)
  	- Check that the application still functions as before

## Deployments
We are currently using a mix of **GitHub Actions** and **Travis CI** for simple build checks and deployments to our environments. We use `CodeCov` to provide reports on test coverage for each Pull Request against the main branches. Over time, our aim is to increase test coverage including unit tests, integration tests, end-to-end tests, and automatic deployments to development process.

We have a CI/CD process set up for deployment to all our environments. On `develop`, any PR that is merged will automatically deploy to our dev environment. Any developer is allowed to deploy their changes to `develop` environment. To request access, contact one of the maintainers.

## Coding conventions

### Naming conventions
- All folder names should only contain lowercase characters.
- All file names should have only lowercase characters and spaces should be substituted with underscores.
 
### Code standards
We'll continue updating this section as our product matures and more standards are established. We welcome any new suggestions!
 
**Django views**
  - Views should be implemented using class-based views instead of function-based views.
 
**Unit tests**
  - We encourage all developers to build unit tests when adding new functionality.
 
**Linting**
  - Code submitted in a PR should be free of linting issues and adhere to `PEP8` standards.
  - The project uses `Flake8` for python code linting.