import git
import os
# rorepo is a Repo instance pointing to the git-python repository.
# For all you know, the first argument to Repo is a path to the repository
# you want to work with
repo = git.Repo("./")
assert not repo.bare
remote = repo.remote()
print(repo.active_branch)
print(repo.working_tree_dir)
print(repo.refs[9])
print(remote.name)

# new_file_path = os.path.join(repo.working_tree_dir, 'testfiled')
# open(new_file_path, 'wb').close()                             # create new file in working tree
# repo.index.add([new_file_path])                        # add it to the index
# # Commit the changes to deviate masters history
# repo.index.commit("Trying out python git push")

# info = remote.fetch()[0]
# print(info.note)
assert remote.exists()

# remote.fetch() 
remote.pull(repo.refs[9])
# remoteInfo = git.remote.push()[0]
# print(remoteInfo.summary)