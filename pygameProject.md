---
marp: true
theme: uncover
class: invert
---

<!--_backgroundColor: black-->

![](https://media.discordapp.net/attachments/1048307606059487304/1061740974595907756/zxc_icon_v2.png)

---

# Концепт

### Прототипом нашего проекта послужила игра "osu!"

---

![width:1080px](https://media.discordapp.net/attachments/1048307606059487304/1061361540785250404/image.png)

---

# Лаунчер

![bg left width:480px height:320px](https://media.discordapp.net/attachments/1048307606059487304/1061359711275991100/image.png)

Умеет:

* Запускать и останавливать игру
* Открыть GitHub
* Открыть инструкцию
* Открыть репорт багов и логи

---

# Технологии лаунчера

* Библиотека PyQt5
* Библиотека subprocess
* Библиотека webbrowser
* Библиотека psutils

Интерфейс - Highly\_Usable\_Interface.py

---

# Начало разработки

[![height:200px](https://media.discordapp.net/attachments/1048307606059487304/1062724222021025873/cf4d7fca34052d4a.png)](https://github.com/EfimkaFeeD/pygameProject/commit/a4fc890b5fbe80c111aad2576dbda1cd8d53a6d0)

---

# Начальное меню

![height:580px](https://media.discordapp.net/attachments/1048307606059487304/1062721303498465290/image.png)

---

![height:650px](https://media.discordapp.net/attachments/1048307606059487304/1062723486046502953/image.png)

---

# Начальная игра

![height:580px](https://media.discordapp.net/attachments/1048307606059487304/1062721396658143302/image.png)

---

# \**Глубокий вдох*\*

Главная программа

```python
2517 | if __name__ == '__main__':
```

![bg right height:300px](https://media.discordapp.net/attachments/1048307606059487304/1062716122111168554/b761bff0f1fabbe2.png)

---

![width:700px](https://media.discordapp.net/attachments/1048307606059487304/1051474630243786802/sticker.webp)

---

# Формула больше-меньше

```python
int(x * (screen_height / 1920))
int(x * (screen_width / 1080))
```

---

# Screeninfo

Масштабирование экрана

```python
from screeninfo import get_monitors

# Необходимо для определения разрешения по неясным причинам
get_monitors()
```

---

# Концепт меню

![height:580px](https://media.discordapp.net/attachments/1048307606059487304/1051921856871010434/menu_concept.png)

---

# Меню

![width:960px](https://media.discordapp.net/attachments/1048307606059487304/1061742543546630194/image_1.png)

---

![width:1080px](https://media.discordapp.net/attachments/1048307606059487304/1061742912565682196/image_2.png)

---

# Настройки

* difficulty
* music
* frame rate
* resolution
* слайдер громкости
* mute
* confirm

---

# Технологии игры

* Библиотека pygame
    * Библиотека pygame_widgets
* Библиотека screeninfo
* Библиотека tkinter
* Библиотека sqlite3
* Библиотека json
* Библиотека logging
* База данных SQLite

---

# Instructions

![height:580px](https://media.discordapp.net/attachments/1048307606059487304/1062727116115935312/image.png)

---

# Account

![height:580px](https://media.discordapp.net/attachments/1048307606059487304/1061360799693684736/image.png)

---

# Stats

![height:580px](https://media.discordapp.net/attachments/1048307606059487304/1061360854685208598/image.png)

---

# Концепт игры

![height:580px](https://media.discordapp.net/attachments/1048307606059487304/1051927979414016061/Figma_35vRaujeX2.jpg)

---

# Игра

![height:580px](https://media.discordapp.net/attachments/1048307606059487304/1061361011791253514/image.png)

---

# Редактор уровней

![height:500px](https://media.discordapp.net/attachments/1048307606059487304/1062755495867318382/image.png)

---

# Окно выбора песни

![height:580px](https://media.discordapp.net/attachments/1048307606059487304/1062729528008527962/image.png)

---

# Главное меню редактора

![height:580px](https://media.discordapp.net/attachments/1048307606059487304/1062737389304434789/image.png)

---

# Диалоговое окно

![height:580px](https://media.discordapp.net/attachments/1048307606059487304/1062737651192573952/image.png)

---

# Окно выбора фона
![height:580px](https://media.discordapp.net/attachments/1048307606059487304/1062737593420230746/image.png)

---

# Live Map Window

![height:580px](https://media.discordapp.net/attachments/1048307606059487304/1062754761327251586/Picsart_23-01-11_18-27-52-348.jpg)

---

# Test Window

![height:580px](https://media.discordapp.net/attachments/1048307606059487304/1062738508822892644/image.png)

---

# Топ коммитов

[:one:](https://github.com/EfimkaFeeD/pygameProject/commit/ad16b7a520c122bac55025b6587e2a61829f5b86) some fix (трилогия)
[:two:](https://github.com/EfimkaFeeD/pygameProject/commit/a51c49fa58a70320878e8ab07a53343f12eb711b) refactor json logic (сколько раз? да [:moyai:](https://media.tenor.com/kHcmsxlKHEAAAAAC/rock-one-eyebrow-raised-rock-staring.gif))
[:three:](https://github.com/EfimkaFeeD/pygameProject/commit/3d0ce8f01c6b6b9bb67b2e237d7f6579cd239665) very minor fixes
[:four:](https://github.com/EfimkaFeeD/pygameProject/commit/f10bb522cad3266fe689bc5e772086ced71abcc9) refactor file system attempt 2 (удалил почти весь проект при первой попытке) 
[:five:](https://github.com/EfimkaFeeD/pygameProject/commit/dae2ed40e0da2d427e07ff9795cb09143ddd344f) remember some files 

---

# GitHub

![height:520px](https://media.discordapp.net/attachments/1048307606059487304/1062736843612897290/1673446602694.jpg)

---

# README.md

Basic GigaChad move [:moyai:](https://github.com/EfimkaFeeD/pygameProject/blob/main/README.md)

![height:480px](https://media.discordapp.net/attachments/1048307606059487304/1062775585144832130/Picsart_23-01-11_19-50-35-971.png)

---

# GitHub Project

![height:580px](https://media.discordapp.net/attachments/1048307606059487304/1062740558495358976/7fda85e62bdc9fb2.png)

---

# GitHub Releases

[![height:440px](https://media.discordapp.net/attachments/1048307606059487304/1062775084214911147/9c1527d4cabde466.png)](https://github.com/EfimkaFeeD/pygameProject/releases/tag/v1.0.0)

---

<!--_backgroundColor: black-->

# Спасибо за внимание[:exclamation:](https://media.discordapp.net/attachments/1048307606059487304/1062767631083515914/2016_04_18_12_04_53_a599bd83bce6598baaa450727aed45c9.png)[:exclamation:](https://media.discordapp.net/attachments/1048307606059487304/1062768109091573800/3474493600513ef9c43c46cc6996efb8.png)

![height:540px](https://media.discordapp.net/attachments/1048307606059487304/1062768530715574373/WPRMrQUOEV8.jpg)