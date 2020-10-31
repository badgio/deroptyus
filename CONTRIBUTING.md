# Git Workflow

When contributing to this repository, please follow the guidelines below.

## Creating your branch

1. Update the **main** and **dev** branches to the latest version.
2. Create new branch.
  - Do it from the branch it will be merged back into (usually **dev**).
  - Prefix it with your initials (eg. `la/auth`).
3. Work peacefully in your branch.

## Pushing changes

4. Pull **dev** to the latest version.
5. Rebase your branch onto **dev**.
6. Squash your local commits.
  - You can do it afterwards, but it is *advisable* to do it before you push it.
7. Push branch to GitHub (origin with the same name)

## Opening a Pull Request

8. After finishing up your feature, open a Pull Request into the **dev** branch.
  - Describe what you did with bullet points.
9. Make sure you added **at least** unit tests.
10. If CI passes, ask for someone to review your PR.

## Code reviewing

11. Make sure you follow the language's conventions.
12. The code owner is responsible for making necessary changes and updating the PR.
13. Wait for one approval before merging into **dev**.

## Merging Code

14. Squash and merge the pull request into the **dev** branch, and delete the branch in the origin.

# Branches

## main

The **main** is sacred. The code is always working and is deployable. **NEVER** work directly on main and never push to it from a local version or from any branch.

## dev

The **dev** is where you branch off and merge in your code. If something does break, you want to fix it as soon as possible.