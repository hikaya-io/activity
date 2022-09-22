# PIP dependencies

We are using [pip-tools](https://github.com/jazzband/pip-tools) for better dependency management.

> All commands are supposed to be executed from your virtual environment!

## Installing dependencies

To install the dependencies into your virtual environment, use the command `pip-sync`.

This will install/upgrade/uninstall everything necessary to match the requirements.txt contents. This way we can ensure all virtual environments perfectly reflect the  `requirements.txt` file.

The generated requirements files will include "transitive dependencies" (dependencies of our dependencies) and show for each dependency metadata of the "why" it was installed as comments.

If you wish to get a clearer picture of the dependency tree, you can use the command `pipedtree`

## Adding a PIP dependency

To add a development or production dependency, use respectively the `dev-requirements.in` and `requirements.in` files. Always **make sure to pin** the version of the dependency.

For this dependency to be added to the `dev-requirements.txt` and `requirements.txt` files, we use `pip-compile`:

```bash
pip-compile requirements.in # Prod dependencies
pip-compile dev-requirements.in # Dev dependencies
```

## Further references

- [jazzband/pip-tools](https://github.com/jazzband/pip-tools)
- [Quick tip: How I use pip-tools to wrangle dependencies](https://www.codementor.io/@adammertz/quick-tip-how-i-use-pip-tools-to-wrangle-dependencies-1fzreskhok)
- [Better Python dependency management with pip-tools](https://cheat.readthedocs.io/en/latest/python/piptools.html)