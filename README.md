# slack-backup-python
Exporting slack channels, conversation using Web API
```source ./bin/activate```
```pip3 install requests```
```pip3 install slack-sdk```

```python3 backup.py --token 'xoxe.xoxp-1-Mi0yLTY1ODAxOTg4NzkyNy01MjQwMTAyMjUxNjE2LTc1NTc3NDIxNTE3MzAtNzU1NzYzOTI3MTMxNS00OWYyMjI1NTkzN2RkYzczMGFjMzNkNDE2Nzg1NmRlMzk1OTk0MzI1ZmZkNjIwMjdlNGQzZDQzMjdmNDA0ZmQ0' --outDir './out'```

Params :
    --token : Slack API access token<br/>
    --outDir : output Directory

### Todo
1. visualizer 
2. add readable date to each message 
3. do not overwrite previous backup