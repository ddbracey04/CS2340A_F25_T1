# CS2340A_F25_T1

## Good Coding Practices and Procedures

### Git Branches
- Each developer should work on their own dedicated user story on a dedicated branch
    - Naming scheme:
        - \[feature/bugfix\]/UserStory#-Brief_Summary_Of_Functionality
            - Using the description on Trello is ideal to keep everything lined up, but any description works as long as user story number is at the start
        - Example: `feature/1-Profile`
        - Example: `bugfix/7-Job_Markers_Not_Appearing`

- If there is a need for main branches (feature/debug) that are not directly tied to any one user story, the same guidelines as above apply with the exception that there will be no UserStory# in the branch name
    - Example: `feature/WebsiteSkeleton`

- If there is a need for a test branch that spawns from another branch, create one with the following guidelines:
    - Naming scheme:
        - your_initials-Summary_Of_Functionality
            - Note: No feature/bugfix tag and no user story number
        - Example: `ddb-map_filter_testing`
    - Test/Debug branches should not need to be around for very long, so try to not do major development on these branches beyond testing/fixing what is needed
        - Once the branch has served its purpose, merge back into its originating branch (not main) and continue developing on that major branch
    

### Committing and Pushing Changes
- Do NOT commit all files (`git commit -a`) without double checking what is being committed
    - Generated files (mainly pycache files) should NOT be in the git repo
    - There should not be too too many changes to go through in this project per commit, so it should not take long
- Local changes should be committed and pushed more frequently rather than less frequently (every 1-2 days of work max is a good bet)
- Commit procedure:
    1. `git status` to check current branch and see what files are changed
    2. If not on right branch, and it needs to be created, run `git checkout -b <BRANCH_NAME>` then proceed
    3. If not on right branch, but it is created, run `git switch <BRANCH_NAME>` then proceed
    4. Choose a file that is listed in the `git status` report, run `git diff <FILE_NAME>`, and verify all changes are correct
        - Note: Diffs can be checked in VSCode's "Source Control" tab by clicking on the file in the "Changes" menu as well
    5. If all the changes are desired/correct, run `git add <FILE_NAME>`
        - Note: Files can be added for commit in VSCode's "Source Control" tab by clicking the '+' next to the file in the "Changes" menu as well
    6. Repeat steps 4-5 for all files listed in red in `git status`, re-running `git status` when desired to check progress
    7. Re-run `git status` one last time to make sure all files desired are included in the commit
    8. Once all file changes are checked and added to the commit, run `git commit -m "<COMMIT_MESSAGE>"`
        - Try to have a descriptive commit message for ease of parsing the commit tree when needed
    9. Run `git push origin <BRANCH_NAME>`
- If a file is accidentally added for commit, run `git restore --staged <FILE_NAME>`
- If a file is accidentally committed, the branch must be rolled back to a previous commit and changes re-committed from there
- If the previous local commit has the wrong info (author, message, missing file, etc.), it can be amended using `git commit --amend --reset-author -m <NEW_MESSAGE>`


### Merges
- No one should merge operational code directly into main unless absolutely necessary due to a time constraint
    - Documentation does not need its own branch, but it is not bad to do so either
- All merges to main should go through a proper PR/MR request procedure (details below)
    - Temporary branches should be merged into other temp branches or major/User Story branches instead of main. PRs/MRs are not needed for these merges.
- PR/MR request procedure
    1. Ensure your branch works independently
    2. Ensure current working code is committed to remote branch (it is pushed)
    3. Run `git pull origin <TARGET_BRANCH>`
        - Note: For PRs/MRs into main, it would be `git pull origin main`
    4. Resolve any merge conflicts
    5. Ensure your branch still works
    6. Commit your branch locally and push to remote
    7. Create the PR/MR in GitHub
        - Make sure to squash the originating branch (if able)
        - It is up to you whether or not to squash commits (merge all commits on the branch into 1 on the main branch), but it is advised to not do so unless there are an inordinate amount of commits on the originating branch
    8. Someone who has not worked on that code should review the code, suggest corrections/fixes/modifications, and mark as reviewed once code is good
    9. Once reviewed and revised, the branch can be merged to main
