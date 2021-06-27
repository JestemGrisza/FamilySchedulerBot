/help for @BotFather
help - Show commands and descriptions
cancel - Cancel any conversation at any place
go - Create task: /go [<day>] <time> <Task description>
go - Create task: /go without args for interactive mode
today - Show list of today tasks
join - Join to bot service and manage join requests
user - List of active users
settings - Bot settings


=========================

Create task

/task|go [<day>] <time> <Task description>

<time>: hh | at hh[:mm] | from hh[:mm] till hh[:mm]

<day>: tomorrow | dd-mm[-yyyy]

<day>:  Monday      | Mon | Mo
        Tuesday     | Tue |	Tu
        Wednesday   | Wed | We
        Thursday    | Thu |	Th
        Friday      | Fri | Fr
        Saturday    | Sat | Sa
        Sunday      | Sun |	Su


Examples:

/go 10 Lunch
/go at 11 gym
/go from 18 till 20 to cinema
/go 17-18 tee

/task tomorrow at 20 Party
/go mon 8 to work
/go fr from 10 till 11 Lunch
/go 25.11


=====================================================
Regular task

/every 10 Lunch


=====================================================
Don't disturb

/ddn == /ddn 1h
/ddn [to 10[.00]]
/ddn [1-23]h
/ddn [1-30]d
/ddn [1-11]m
/ddn [1-100]y

==========
Ask all to take Task)

/ask [<day>] <time> <Task description>

==========
Show table of today tasks

/today
/today <user>
/today all

===========
Set and show family Time Zone (Default is UTC)

/tz
/tz Europe/Kiev
/tz +2:00
/tz geo

=====================================================
=====================================================



Ukrainian, Russian and other lang on the way!

=====================================================



/го [<день>] <время> <Задание>

<время>: чч |в чч[:мм] | с чч[:мм] до чч[:мм]
<день>: завтра | послезавтра | ДД-ММ[-ГГГГ]
<день>: Понедельник    | Пн
        Вторник        | Вт
        Среда          | Ср
        Четверг        | Чт
        Пятница        | Пт
        Суббота        | Су
        Воскресенье    | Вс
        Выходные       | Вых

/каждый Пон в 8

/нах == /нах 1ч
/нах [до 10[.00]]
/нах [1-23]ч
/нах [1-30]д
/нах [1-11]м
/нах [1-100]г
