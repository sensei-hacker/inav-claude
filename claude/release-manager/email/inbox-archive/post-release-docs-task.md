# Post-Release Task: Publish Release Documentation

**Priority:** After 9.0.0-RC2 release is complete

## Task

1. Add a note to `claude/release-manager/README.md` stating it is designed for use with an automated assistant
2. Copy the file to `inav/docs/development/Release-Creation.md`
3. Create a branch off master in inav repo
4. Commit without mentioning Claude
5. Create PR to upstream

## Commands

```bash
# Add note to README (edit the file first)

# Then copy and PR
cd inav
git checkout master && git pull
git checkout -b docs-release-creation-guide
cp ../claude/release-manager/README.md docs/development/Release-Creation.md
git add docs/development/Release-Creation.md
git commit -m "Add release creation guide to documentation"
git push -u origin docs-release-creation-guide
gh pr create --repo iNavFlight/inav --title "Add release creation guide"
```

## Status

- [ ] 9.0.0-RC2 release completed
- [ ] Documentation updated and PR created
