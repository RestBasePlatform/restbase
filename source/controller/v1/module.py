import datetime
import glob
import json
import os
import shutil
import tarfile
from typing import List

import git
import requests
import yaml
from models import InstalledModules


def get_link_for_raw_file(link: str) -> str:
    link = link.replace("/blob", "")
    return link.replace("github", "raw.githubusercontent")


def get_module_config_from_github(
    repo_link: str, version: str = "stable", version_file="restabse_cfg.yaml"
) -> dict:

    version_branch_converter = {"stable": "master"}

    file_link = (
        repo_link.replace("/blob", "").replace("github", "raw.githubusercontent")
        + "/"
        + version_branch_converter.get(version, "master")
        + "/"
        + version_file
    )
    r = requests.get(file_link)
    return yaml.load(r.text)


def install_module_from_github(github_url: str, db_connection):

    module_config = get_module_config_from_github(github_url)

    if not module_config:
        raise ValueError()

    if module_config["module_name"] not in [i["module_name"] for i in list_modules()]:
        raise ModuleNotFoundError(f"Module '{module_config['module_name']}' not found")

    clone_path = f"modules/{module_config['module_name']}/{module_config['version']}"

    if not os.path.exists(clone_path):
        os.makedirs(clone_path)
    else:
        raise Exception(
            f"Module {module_config['module_name']} version {module_config['version']} already installed"
        )

    git.Git(clone_path).clone(github_url)

    # Git library creates sub folder automatically
    # Need to move all files from it
    module_dir_name = os.listdir(clone_path)[0]

    source_dir = clone_path + "/" + module_dir_name
    dst = clone_path
    files = glob.iglob(os.path.join(source_dir, "*"))
    for file in files:
        if os.path.isfile(file):
            shutil.move(file, dst)

    shutil.rmtree(clone_path + "/" + module_dir_name)

    new_module = InstalledModules(
        id=module_config["module_name"] + str(module_config["version"]),
        module_name=module_config["module_name"],
        version=module_config["version"],
        installation_date=datetime.datetime.now(),
    )
    db_connection.add(new_module)
    db_connection.commit()

    return f"Module {module_config['module_name']} successfully installed"


def remove_module(
    module_name: str, version: str, db_connection, all_versions: bool = False
):
    module = (
        db_connection.query(InstalledModules)
        .filter_by(id=module_name + version)
        .first()
    )

    if not os.path.exists("modules/" + module_name + "/" + version):
        raise Exception(
            Exception(f"Module {module_name} version {version} is not installed")
        )

    shutil.rmtree("modules/" + module_name + "/" + version, ignore_errors=True)

    if all_versions:
        os.rmdir("modules/" + module_name)

    db_connection.delete(module)
    db_connection.commit()

    return f"Module {module_name} successfully removed"


def install_from_release(module_name: str, release_tag: str, db_connection):
    releases_answer = json.loads(
        requests.get(
            f"https://api.github.com/repos/RestBaseApi/{module_name}/releases"
        ).text
    )

    download_tar_url = None
    for release in releases_answer:
        if release["tag_name"] == release_tag:
            download_tar_url = release["tarball_url"]

    if not download_tar_url:
        raise ValueError(f"Release {module_name} with tag {release_tag} not found")

    r = requests.get(download_tar_url, stream=True)

    if r.status_code == 200:
        path = f"modules/{module_name}/{release_tag}"

        archive_path = path + "/archive.tgz"
        if not os.path.exists(path):
            os.makedirs(path)
        else:
            raise Exception(
                f"Module {module_name} version {release_tag} already installed"
            )
        with open(archive_path, "wb") as f:
            f.write(r.raw.read())
    else:
        raise ConnectionError("Error with download. Try again later.")

    tar = tarfile.open(archive_path, "r:gz")
    tar.extractall(path=path)
    tar.close()

    source_dir = path + "/" + os.listdir(path)[1]
    dst = path
    files = glob.iglob(os.path.join(source_dir, "*"))
    for file in files:
        if os.path.isfile(file):
            shutil.move(file, dst)

    shutil.rmtree(source_dir)
    # TODO: Replace with remove method from os (why it cause error???)
    os.system(f"rm {archive_path}")

    new_module = InstalledModules(
        id=module_name + release_tag,
        module_name=module_name,
        version=release_tag,
        installation_date=datetime.datetime.now(),
        functions={"test": "test"},
    )
    db_connection.add(new_module)
    db_connection.commit()

    return f"Module {module_name} successfully installed"


def list_modules(org_name="RestBaseApi") -> List[dict]:
    answer = json.loads(
        requests.get(f"https://api.github.com/orgs/{org_name}/repos").text
    )
    module_names = [i["name"] for i in answer if i["name"].endswith("Module")]

    available_modules = []

    for module_name in module_names:
        releases_answer = json.loads(
            requests.get(
                f"https://api.github.com/repos/RestBaseApi/{module_name}/releases"
            ).text
        )

        for release in releases_answer:
            available_modules.append(
                {
                    "module_name": module_name,
                    "version": release["tag_name"],
                    "release_date": release["published_at"],
                }
            )
    return available_modules


def list_installed_modules(db_connection) -> List[dict]:
    return [i.to_dict() for i in db_connection.query(InstalledModules)]
