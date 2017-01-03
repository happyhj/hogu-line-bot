# hogu-line-bot

## Getting started

### pre-commit hook 세팅 (파이썬 컴파일 실패시 커밋안됨)
로컬에서 개발 시 필수 작업
배포 후에 문법에러나면 짜증나므로 개발전에 먼저 아래 커맨드를 실행시키자 

```
$ cp ./tmp/pre-commit ./.git/hooks/pre-commit 
$ tr -d '\r' < ./tmp/pre-commit > ./.git/hooks/pre-commit
```

### 배포

커밋하고 

```
$ git push origin master
```

성공하면 알아서 

heroku 의 line web bot 서버에 배포됨

### 서버 로그 보는 법 

heroku 가입 한 후 가입이메일을 오너에게 알려 heroku 서버 권한들 등록받아야함
권한등록이 끝난 후 [heroku cli 를 설치](https://devcenter.heroku.com/articles/heroku-cli) 한 다음 아래 커맨드를 실행한다.
```
$ heroku logs --app hogu-line-bot
```


### 아래는 로컬에서 실행하지 않는 경우에는 의미 없는 경우이다
```
$ export LINE_CHANNEL_SECRET=YOUR_LINE_CHANNEL_SECRET
$ export LINE_CHANNEL_ACCESS_TOKEN=YOUR_LINE_CHANNEL_ACCESS_TOKEN

$ pip install -r requirements.txt

```

Run WebhookParser sample

```
$ python app.py
```

Run WebhookHandler sample

```
$ python app_with_handler.py
```
