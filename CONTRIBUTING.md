_UPDATED: 20221001_

# Ground rules and expectations
 
Before we get started, here are a few things we expect from you (and that you should expect from others):
 
- Be kind and thoughtful in your conversations around this project. We all come from different backgrounds and projects, which means we likely have different perspectives on "how open source is done." Try to listen to others rather than convince them that your way is correct.
- Activity Community Versions are released with a [Contributor Code of Conduct](./CODE_OF_CONDUCT.md). By participating in this project, you agree to abide by its terms.
- If you open a pull request, please ensure that your contribution passes all tests. If there are test failures, you will need to address them before we can merge your contribution.
- When adding content, please consider if it is widely valuable. Please don't add references or links to things you or your employer have created as others will do so if they appreciate it.

# How to contribute
 
Thanks for checking out **Activity**. Activity is an open source project currently maintained by the team at [Hikaya](https://hikaya.io/team). All contributors are welcome to submit issues and make pull requests to the repository.

If you'd like to contribute, start by searching through the [issues](https://github.com/hikaya-io/activity/issues) and [pull requests](https://github.com/hikaya-io/activity/pulls) to see whether someone else has raised a similar idea or question. To get started with a simple issue, you can checkout the issues labeled `good first issue`. If you see none, feel free to create an issue and ask for guidance on where to start.

- If you find an issue you would like to work on, feel free to write a comment on the issue and ask to be assigned.
- If you don't find one you would like to work on, create an issue, assign a label and @mention one of the maintainers to let them know about the issue.

## Contribution review process

This repo is currently maintained by the team at [Hikaya](https://hikaya.io/team/), who have `maintainer` access. They will likely review your contribution. If you haven't heard from anyone in 5 days, feel free to bump the thread or @mention a maintainer to review your contribution.

## Tips on how to get the most out of contributing

1. **Determine how many hours you can commit to each week.** Think about how many hours you can commit to each week. Currently many of our contributors spend around ~20-25 hours a week but there is no minimum, only that you set your own hours.
2. **Come up with your own weekly schedule and propose it to the team.** If you have certain days and times you are tentatively available you can put together a schedule of what a typical week will look like so others can try and sync with you or know when to reach out on slack. These  are just tentative and used by other contributors to coordinate calls between each other.
3. **Try to make at least one of the sprint calls each week (Monday and Saturday 7 PM EAT).** If you can’t make a call, kindly write on the #sprint-planning slack channel or message me before hand so we can know if you are able to join or not. We just ask for communication courtesy but understand contributors won’t be able to make each call.
4. **Ask for help when you need it** Our philosophy is to let contributors work on anything they think could add value to our apps. The core team at Hikaya will try to make themselves available to support any new onboarding or even have paired programming sessions on an issue to help you get started. We kindly ask all contributors to not be shy and ask for help when you need it.
5. **Be open and communicate** If life has gotten busy or priorities have changed and you can no longer contribute, no worries, we completely understand! All we ask is for you to communicate and let us know upfront so we can plan accordingly. You're always welcome to pause and contribute another time.

## Community

Discussions about Dots take place in the `Issues` as well as in [Discussions](https://github.com/hikaya-io/activity/discussions). Anybody is welcome to join these conversations.

Thanks for contributing!

---

# How we manage our code

**Source control:** Git

**Source code:** This project is stored in [GitHub](https://github.com/hikaya-io/activity).

**Branches:**

We use 3 types of branches in all our repositories :

`develop` - All bug fixes, defects, and tasks.<br>
`Feature branches`: All feature branches must be named like `123-explanation-of-feature-fix`, where 123 is the issue number on GitHub.<br>
`main` - Clean code in production environment<br>

> **Note:**
> * All pull requests should be based off of the `develop` branch.

## Commits

We use Github to track **Issues** and **Pull Requests** for all our work. When making commits, please ensure that you have created a separate branch off of the `develop` branch before you begin making changes to the source code.

Feel free to make commits as often as possible to your branch. If the issue you are working on has been open for a few days, consider rebasing your branch to `develop` branch get the latest changes before you create a Pull Request. This will help you avoid merge conflicts when raising your Pull Request.

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

Once you have pushed code and your branch to Github, you can open a Pull Request. There are two types of Pull Requests: *Work in progress (WIP)* and *Ready for review*. Each type has a label you can use to mark it as `WIP` or `Ready for review`. Feel free to create a WIP Pull Request for larger features that require additional input from other contributors or is a research/proof of concept task.

Here are some guidelines for making Pull Requests:
- All developers MUST submit Pull Requests for any change made on any of the Hikaya Repositories.
- The Pull RequestR must be reviewed by at least **1 developer** other than the author. In addition, you can ask for a user testing review by @mentioning a member of the product and QA team.
- Before opening a Pull Request, we suggest you to consider the following steps first:
  - [ ] Check that the application still functions locally as before
  - [ ] All set checks pass
  - [ ] The bug/feature/enhancement in question is fully addressed and satisfies the issue acceptance criteria
- When you're ready to open a Pull Request, you can use the predefined template to help you document your Pull Request. In the Pull Request body, the following questions should be addressed:

  - **Descriptive Title:** Add the issue number followed by a brief description of the ticket e.g., `DOTS-001: Adds project status`
  - **What issue(s) does this Pull Request resolve?** *List all the issues resolved by this Pull Request*
    - [ ] Issue 1

    Type the following to automatically link the issue to this PR: `Resolves _[Github Issue #](https://example.com/ABCD-XXXX)_`

    > If this PR is still a `work in progress`, add the label = `WIP`.
  - **Considerations and implementation** Describe the approach you took to solve the issue and mention any issues that others should pay attention to.
  - **How to test** List the steps for others to test your changes.
    - [ ] Step 1
  - **Test(s) added** List the tests you've added or need to be added:
    - [ ] Test 1
  - **Mentions?** @mention the people you'd like to review this Pull Request

## Deployments

We are currently using **GitHub Actions** for build checks and deployments to our development and production environments.

We use `CodeCov` to provide reports on test coverage for each Pull Request against the main branches. Over time, our aim is to increase test coverage including unit tests, integration tests, end-to-end tests, and automatic deployments to development process.

We have a CI/CD process set up for deployment to all our environments. On `develop`, any Pull Request that is merged will automatically deploy to our development environment. Any developer is allowed to deploy their changes to `develop` environment. To request access, contact one of the maintainers.

## QA testing

We perform QA testing when features are merged into `develop`. We use automated end-to-end testing by [Cypress](https://www.cypress.io/) to provide a strong foundation for functional testing.

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
