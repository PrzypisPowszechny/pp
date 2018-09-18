annotation_priorities = (
    ('NORMAL', 'normalny'),
    ('WARNING', 'ostrzegawczy'),
    ('ALERT', 'niebezpieczny'),
)

SUGGESTED_CORRECTION = 'SUGGESTED_CORRECTION'

annotation_report_reasons = (
    ('BIASED', 'nieobiektywny'),
    ('UNRELIABLE', 'nierzetelne źródło'),
    ('USELESS', 'niepotrzebny'),
    ('SPAM', 'spam'),
    ('OTHER', 'inne'),
    (SUGGESTED_CORRECTION, 'sugerowana poprawka'),
)

PP_PUBLISHER = 'PP'
DEMAGOG_PUBLISHER = 'DEMAGOG'

PUBLISHERS = (
    (PP_PUBLISHER, 'Przypis Powszechny'),
    (DEMAGOG_PUBLISHER, 'Demagog'),
)