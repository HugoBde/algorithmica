import os
from typing import List


class MyFile:
    def __init__(self, dir, name) -> None:
        self.dir = dir
        self.name = name

        with open(f"{dir}/{name}", "r") as f:
            lines = f.readlines()
            frontmatter = False

            for line in lines:
                if "---" in line:
                    if frontmatter:
                        return
                    else:
                        frontmatter = True
                elif line.startswith("weight: "):
                    self.weight = int(line.removeprefix("weight: "))
                elif line.startswith("draft: true"):
                    raise Exception("draft")

        if self.weight is None:
            raise Exception("Missing weight")

    def __str__(self) -> str:
        return f"{self.dir}/{self.name}"

    def get_content(self) -> str:
        with open(f"{self.dir}/{self.name}", "r") as f:
            lines = f.readlines()
            frontmatter = False
            for i in range(len(lines)):
                if "---" in lines[i]:
                    if frontmatter:
                        return "".join(lines[i + 2 :])
                    else:
                        frontmatter = True

        raise Exception("no frontmatter")


class MyDir:
    def __init__(self, path: str) -> None:
        self.path = path
        self.chapter_id = path.removeprefix("./")
        self.files: List[MyFile] = []
        self.title = ""

        with open(f"{path}/_index.md") as f:
            lines = f.readlines()
            frontmatter = False

            for line in lines:
                if "---" in line:
                    if frontmatter:
                        break
                    else:
                        frontmatter = True
                elif line.startswith("weight: "):
                    self.weight = int(line.removeprefix("weight: "))
                elif line.startswith("draft: true"):
                    raise Exception("draft")
                elif line.startswith("title: "):
                    self.title = line.removeprefix("title: ")

        if self.weight is None:
            raise Exception("Missing weight")

        for entry in os.listdir(self.path):
            if entry != "_index.md" and os.path.isfile(f"{self.path}/{entry}"):
                try:
                    file = MyFile(self.path, entry)
                    self.add_file(file)
                except Exception as e:
                    print(f"Skipping file {self.path}/{entry}: {e}")

        self.sort_files()

    def __str__(self) -> str:
        return f"{self.path} :: {self.title}"

    def add_file(self, file: MyFile) -> None:
        self.files.append(file)

    def sort_files(self) -> None:
        self.files = sorted(self.files, key=lambda f: f.weight)

    def get_content(self) -> str:
        content = ""

        with open(f"{self.path}/_index.md", "r") as f:
            lines = f.readlines()
            frontmatter = False
            for i in range(len(lines)):
                if "---" in lines[i]:
                    if frontmatter:
                        content += "".join(lines[i + 2 :])
                    else:
                        frontmatter = True

        for file in self.files:
            try:
                content += file.get_content()
            except Exception as e:
                print(f"{file}: {e}")

        content = content.replace("../img", "img")
        content = content.replace("img/", f"{self.path}/img/")
        content = content.replace("\u2502", "|")
        content = content.replace("[^", f"[^{self.chapter_id}")

        return content


chapters: List[MyDir] = []

# get all dirs
for entry in os.listdir("."):
    path = f"./{entry}"
    if os.path.isdir(path):
        try:
            dir = MyDir(path)
            chapters.append(dir)
        except Exception as e:
            print(f"Skipping directory {path}: {e}")


def extract_content(dir, file):
    with open(path, "r") as f:
        lines = f.readlines()

    front_matter_started = False
    start = 0

    for i in range(len(lines)):
        if "---" in lines[i]:
            if front_matter_started:
                start = i + 2
                break
            else:
                front_matter_started = True

    content = "".join(lines[start:])

    if file == "_index.md":
        content = content.replace("img/", f"{dir}/img")
    else:

        content = content.replace("../img/", f"{dir}/img")

    return content


chapters.sort(key=lambda d: d.weight)
source = ""

print("\n\n Table of Content:\n")

for chapter in chapters:
    print(f"\n\n{chapter}")
    for file in chapter.files:
        print(file)
    source += chapter.get_content()

with open("source.md", "w") as output:
    output.write(source)
