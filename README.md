<h1 align="center">
    CodingLovers Management Bot
</h1>
<p align="center">
    <em>A Simple Group Manager | Designed for t.me/CodingLovers_GP</em>
</p>

> ![WARNING]\
> This bot is in testing process and not completely tested.

## Features
- Useful user management operations such as mute, ban, etc.
- A simple warning system.
- Support trusted users and the special votekick system.
- and so on ..

## Using source
1. First of all clone this repository code ...

```bash
git clone https://github.com/awolverp/codingloversbot
rm -rf .git
```

2. On second step, you have to customize the settings. Rename the `settings-sample.yml` to `settinsg.yml` and then edit it.

3. Now we have two ways for running the bot.

    1. You can easily use docker to run:

    ```python
    docker compose build
    docker compose up -d
    ```

    2. Using python with *screen* or *tmux* tools.

    ```python
    # Create the screen or tmux session and then:
    python3 manage.py
    ```
