def not_a_trainer_test(user):
    return not user.groups.filter(name="Trainer").exists()


def trainer_test(user):
    return user.groups.filter(name__in=["Trainer", "Executive"]).exists()


def frontdesk_test(user):
    return user.groups.filter(name__in=["Trainer", "Executive"]).exists()


def executive_test(user):
    return user.groups.filter(name="Executive").exists()
