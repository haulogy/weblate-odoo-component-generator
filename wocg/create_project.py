# -*- coding: utf-8 -*-
# Copyright 2018 ACSONE SA/NV (<http://acsone.eu>)

from wocg.tools.git_utils import git_clone
from wocg.tools.helper import get_component_slug, get_component_name
from wocg.tools.logger import get_logger
from wocg.tools.manifest import get_translatable_addons

import click
import os
import re
import django
django.setup()

from weblate.addons.models import Addon
from weblate.trans.models import Project, Component

logger = get_logger()


def get_project_name(repository, branch):
    repo_name = repository.split('/')[-1].replace('.git', '')
    return '%s-%s' % (repo_name, branch)


def get_project_slug(project_name):
    project_slug = re.sub("[^A-Za-z0-9-]", "-", project_name)
    return project_slug


def create_project(
        repository, branch, tmpl_component_slug, addons_subdirectory=None):
    project_name = get_project_name(repository, branch)

    logger.info("Project name is %s" % project_name)

    try:
        Project.objects.get(name=project_name)
        logger.info("Project %s already exists." % project_name)
    except Project.DoesNotExist:
        repo_dir = git_clone(repository, branch)
        addons = get_translatable_addons(
            repo_dir, addons_subdirectory=addons_subdirectory)

        if not addons:
            logger.info("No addons found in %s %s" % (repository, branch))
            return

        logger.info("Going to create Project %s." % project_name)
        addon_name = next(iter(addons.keys()))
        new_project = get_new_project(project_name, repository)

        try:
            get_new_component(
                new_project, repository, branch, addon_name,
                tmpl_component_slug,
                addons_subdirectory=addons_subdirectory)
        except Exception as e:
            logger.exception(e)
            new_project.delete()


def get_new_project(project_name, url):
    new_project = Project()
    new_project.name = project_name
    new_project.slug = get_project_slug(project_name)
    new_project.web = url
    new_project.enable_review = True
    new_project.set_translation_team = False
    new_project.save()
    return new_project


def get_new_component(
        project, repository, branch, addon_name, tmpl_component_slug,
        addons_subdirectory=None):
    po_file_mask = '{}/i18n/*.po'.format(addon_name)
    pot_filepath = '{addon_name}/i18n/{addon_name}.pot'.format(
        addon_name=addon_name)
    if addons_subdirectory:
        po_file_mask = os.path.join(addons_subdirectory, po_file_mask)
        pot_filepath = os.path.join(addons_subdirectory, pot_filepath)
    tmpl_component = Component.objects.get(slug=tmpl_component_slug)
    addons_to_install = Addon.objects.filter(component=tmpl_component)

    new_component = tmpl_component
    new_component.pk = None
    new_component.project = project
    new_component.name = get_component_slug(project, addon_name)
    new_component.slug = get_component_name(project, addon_name)
    new_component.repo = repository
    new_component.push = repository
    new_component.branch = branch
    new_component.filemask = po_file_mask
    new_component.new_base = pot_filepath
    new_component.file_format = 'po'
    new_component.save(force_insert=True)

    for addon_to_install in addons_to_install:
        addon_to_install.pk = None
        addon_to_install.component = new_component
        addon_to_install.save()
    return new_component


@click.command()
@click.option(
    '--repository', required=True,
    help="ssh url to git repository",
)
@click.option(
    '--branch', required=True,
    help="Target branch"
)
@click.option(
    '--tmpl-component-slug', required=True,
    help="SLUG identifier for the template component"
)
@click.option(
    '--addons-subdirectory',
    help="Addons directory"
)
def main(repository, branch, tmpl_component_slug, addons_subdirectory=None):
    """
    This program initializes a weblate project based on git repository.
    The Git repository should contains at least one installable addons
    with a i18n repository containing the .pot file, otherwise it does nothing.
    """
    create_project(
        repository, branch, tmpl_component_slug,
        addons_subdirectory=addons_subdirectory)
