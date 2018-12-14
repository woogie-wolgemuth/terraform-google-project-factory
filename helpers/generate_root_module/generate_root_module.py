#!/usr/bin/env python

import subprocess
import sys
import hcl


def boilerplate():
    """
    Generate common boilerplate for a Terraform file.

    Returns:
        str: The evaluated boilerplate.
    """
    with open("./test/boilerplate/boilerplate.tf.txt") as fh:
        buf = fh.read()
        buf += "\n\n"
        buf += "// File autogenerated by " + \
               "`helpers/generate_root_module/generate_root_module.py`\n"
        return buf


def main_tf(variables):
    """
    Generate the root level `main.tf`.


    Args:
        variables (map[str, map[str, str]]): A list of variables to pass from
            the root module to the core_project_factory module.

    Returns:
        str: The contents of the file `main.tf`.
    """

    buf = boilerplate()
    buf += """

module "project-factory" {
  source = "modules/core_project_factory"

"""

    for varname in variables:
        buf += '%s = "${var.%s}"\n' % (varname, varname)

    buf += "}\n"

    return buf


def outputs_tf(outputs):
    """
    Generate the root level `outputs.tf`.

    Args:
        outputs (map[str, map[str, str]]): A map of parsed outputs from the
            core_project_factory module.

    Returns:
        str: The contents of `outputs.tf`
    """
    buf = boilerplate()
    buf += "\n\n"

    for name, attrs in outputs.items():
        desc = attrs.get("desc", None)

        buf += 'output \"%s\" {\n' % name
        buf += 'value = "${module.project-factory.%s}"\n' % name

        if desc:
            buf += 'description = "{0}"\n' % desc

        buf += "}\n"

    return buf


def main(argv):
    with open("./modules/core_project_factory/variables.tf") as fh:
        variables_text = fh.read()
        variables = hcl.loads(variables_text)['variable']

    with open("./modules/core_project_factory/outputs.tf") as fh:
        outputs = hcl.load(fh)['output']

    with open("./variables.tf", "w") as fh:
        # Copy `variables.tf` without modification
        fh.write(variables_text)

    with open("main.tf", "w") as fh:
        fh.write(main_tf(variables))

    with open("outputs.tf", "w") as fh:
        fh.write(outputs_tf(outputs))

    subprocess.call(["terraform", "fmt"])


if __name__ == "__main__":
    main(sys.argv)
