# Form Library

> This is work in progress

## Github Issues reference

Here is a short list of Github issues related to `formlibrary`.
They have specifications about the models, their attributes and the relations between them:

1. Create a [Service model](https://github.com/hikaya-io/activity/issues/412)
2. Update [Distribution](https://github.com/hikaya-io/activity/issues/419) and [Training](https://github.com/hikaya-io/activity/issues/421) models
3. Adjust fields in [Individual model](https://github.com/hikaya-io/activity/issues/403)
4. Create [Case model](https://github.com/hikaya-io/activity/issues/410)
5. Create [Household model](https://github.com/hikaya-io/activity/issues/409)
6. Create [Attendance models](https://github.com/hikaya-io/activity/issues/422)
7. Create [Inventory model](https://github.com/hikaya-io/activity/issues/418)

> Please feel free to update the list above :point_up: !

## Models

### Current state

Models are gathered inside the directory `models` and [organized as a package](https://docs.djangoproject.com/fr/2.2/topics/db/models/#organizing-models-in-a-package).

If you add models to the folder, just make sure to expose your model in `__init__.py`.


- `Service` is marked as an abstract class, since a service can't exist without being one, and only one, of the supported service types (`Training`, `Distribution`...).

- `Case` is a parent model for `Individual` and `Household`

### Models relationships

Since much refactoring is planned, it is important to keep track of the relationships of the models, especially with models of other Django applications applications:

Individual:

    ===> workflow/SiteProfile
    ===> workflow/Program
    ===> TrainingAttendance
    ===> Distribution

Distribution:

    ===> workflow/Program
    ===> workflow/ProjectAgreement
    ===> workflow/Office
    ===> workflow/Province

> Note: All links to external models are with the `workflow` app

## Tests

We are opting to write tests as we code, or even better, before coding ([Test Driven Development](https://www.obeythetestinggoat.com/book/part1.harry.html))

If you are not familiar with writing tests, then no worries. They can be written separately by a reviewer.

> TODO add guideline to writing tests

### Testing and fixtures

Fixtures can be used for tests too. It would allow us to avoid the usual boilerplate code in tests where model instances are created.
This way, we can fetch already existing objects, and define the relationships between them.
