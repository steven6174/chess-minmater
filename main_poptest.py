from py_pushover_simple import pushover


def main():
    p = pushover.Pushover()
    p.user = 'u8n6jgf7o7cmrp3hqgccketo3yzvr8'
    p.token = 'a238k1itun6srze21gsnk24jofo366'
    p.send_message('hi there')


if __name__ == '__main__':
    main()
