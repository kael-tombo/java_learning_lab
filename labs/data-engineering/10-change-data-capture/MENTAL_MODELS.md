# Mental Models for CDC

## 1. The Security Camera
- **Database log** = Security footage (everything recorded)
- **Debezium** = Camera system reading the footage
- **Kafka** = Video feed to monitoring stations
- **Snapshot** = Initial photo of the scene
- **Streaming** = Live footage after initial photo

## 2. The Journalist's Notebook
- **Transaction log** = Reporter's raw notes
- **CDC** = Editor reviewing and publishing notes
- **Kafka** = Newspaper printing press
- **Consumers** = Readers getting updates
- **Outbox** = Press release (intentional publication)

## 3. The Git Repository
- **Database** = Git repo files
- **Transaction log** = Git commit log
- **CDC** = git log --follow
- **Snapshot** = git checkout (specific point in time)
- **Changes** = git diff between commits
