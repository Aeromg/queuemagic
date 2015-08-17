# -*- coding: utf-8 -*-
__author__ = 'vdv'

config = {
    'ldap': {
        'dc': 'dc.tld',
        'user': 'username',
        'password': 'password',
        'catalog': 'ou=Users,dc=dc,dc=tld',
        'strings': {
            'default_email_domain': 'dc.tld',
            'xmpp_domain': 'dc.tld'
        },
        'wildcard_mail_field': 'mail',
        'xmpp_field': 'jid',
        'local_domains': [
            'dc.tld',
            'some.tld'
        ],
        'cache': {
            'path': '{{app.cache}}/ldap',
            'ttl': 60 * 5,  # 5 minutes
            'prefix': '',
        },
        'extra_fields': [
            'skype',
            'icq',
            'logo',
            'avatar'
        ],
        'extra_fields_source': 'info'
    },
    'templates': {
        'store': '{{app.lib}}/templates',
        'filters': [
            'modules.services.templates.filters'
        ],
        'map': {
            'full_html': '{{app.lib}}/templates/disclaimer_full.html',
            'light_html': '{{app.lib}}/templates/disclaimer_light.html',
            'full_plain': '{{app.lib}}/templates/disclaimer_full.txt',
            'light_plain': '{{app.lib}}/templates/disclaimer_light.txt',
            'vcf': '{{app.lib}}/templates/businesscard.vcf',
            'sender_fullname': '{{app.lib}}/templates/auth_sender_fullname.txt'
        },
        'view_bag': {
            'web_site': 'http://www.dc.tld'
        }
    },
    'statistics': {
        'persistent': {
            'db': '{{app.lib}}/statistics.db'
        }
    },
    'dkim': {
        'headers': [
            'Date', 'From', 'Reply-To', 'To', 'Subject'
        ],
        'selector': 'mail',
        'default_domain': {
            'private_key': '{{app.lib}}/domain_keys/{domain}/mail.private',
            'enabled': True,
            'selector': 'mail'
        },
        'domains': [
            {
                'name': 'dc.tld',
                'private_key': '/home/devel/dc.tld.pem',
                'with_subdomains': True
            }
        ]
    },
    'attachments': {
        'path': '{{app.lib}}/attachments'
    },
    'cache': {
    },
    'pipelines': {
        'empty': {
            'queue': []
        },
        'disclaimer_full': {
            'stages': {
                'logo': {
                    'module': 'logo_inject',
                    'default': 'logo_72.png',
                    'avatar': 'avatar',
                    'display': 'logo.png',
                    'id': 'logo'
                },
                'vcard': {
                    'module': 'vcard_inject',
                    'template': 'vcf',
                    'display': 'vcard.vcf',
                    'encoding': 'cp1251'
                },
                'disclaimer': {
                    'html': 'full_html',
                    'plain': 'full_plain'
                }
            },
            'queue': [
                'logo',
                'vcard',
                'disclaimer',
            ],
            'error': 'continue'
        },
        'disclaimer': {
            'stages': {
                'switch': {
                    'if': {
                        'statistics': {
                            'first_time': True,
                            'antiquity': '{{env.dialog_antiquity}}'
                        }
                    },
                    'then': {
                        'module': 'chain',
                        'jump': 'disclaimer_full'
                    },
                    'else': {
                        'module': 'disclaimer',
                        'html': 'light_html',
                        'plain': 'light_plain'
                    }
                }
            },
            'queue': [
                'switch'
            ],
            'error': 'continue'
        },
        'postfix': {
            'filter': {
                'auth': {
                    'sender_location': 'internal'
                },
                'attrib': {
                    'with_referenced': False
                },
                'aggregate': 'all'
            },
            'stages': {
                'disclaimer_chain': {
                    'filter': {
                        'hashtag': {
                            'tags': [
                                u'nodisclaimer'
                            ],
                            'take': 'all',
                            'negation': True
                        }
                    },
                    'module': 'chain',
                    'jump': 'disclaimer',
                    'resume': True
                },
                'beautifulizer': {
                    'locations': ['subject', 'body'],
                    'remove_long_spaces': True,
                    'remove_long_newline': True,
                    'remove_html': False,
                    'restore_punctuation': True,
                    'sender_name_rewrite': lambda x: u'{0} {1}'.format(x.identity.first_name, x.identity.last_name),
                },
                'isolator': {
                    'filter': {
                        'hashtag': {
                            'tags': [
                                u'spam'
                            ],
                            'take': 'any',
                            'locations': ['subject']
                        }
                    },
                    'undisclosed': False
                },
                'remove_hashtag': {
                    'filter': {
                        'hashtag': {}
                    }
                },
                'header': {
                    'name': 'X-Content-Filter',
                    'value': '{{app.full_name}} the {{app.description}}'
                },
                'dkim': {
                    'module': 'dkim'
                }
            },
            'queue': [
                'beautifulizer',
                'disclaimer_chain',
                'isolator',
                'remove_hashtag',
                'header',
                'dkim'
            ],
            'error': 'continue'
        }
    },
    'services': {
        'Logs': {
            'fabric': 'modules.services.logs.file_logs_fabric.FileLogsFabric',
            'config': {
                'level': 'debug',
                'file': '/var/log/queuemagic.log',
                'newline': '\r\n'
            },
            'single': True
        },
        'AuthoritySource': {
            'fabric': 'modules.services.identification.fabric.ActiveDirectoryFabric',
            'config': '{{ldap}}'
        },
        'Attachments': {
            'fabric': 'modules.services.attachments.fabric.AttachmentsFabric',
            'config': '{{attachments}}'
        },
        'Cache': {
            'fabric': 'modules.services.cache.fabric.FileCacheFabric',
            'config': '{{cache}}'
        },
        'DomainKeysSigner': {
            'fabric': 'modules.services.domain_keys.fabric.DomainKeysSignerFabric',
            'config': '{{dkim}}'
        },
        'TextFactory': {
            'fabric': 'modules.services.templates.fabric.TextFactoryFabric',
            'config': '{{templates}}'
        },
        'PipelineService': {
            'fabric': 'modules.services.pipeline.fabric.PipelineServiceFabric',
            'config': '{{pipelines}}'
        },
        'ModulesResolver': {
            'fabric': 'modules.services.modules.fabric.ModulesResolverFabric',
            'config': '{{modules}}'
        },
        'Speller': {
            'fabric': 'modules.services.speller.yandex_speller_fabric.YandexSpellerFabric',
            'config': '{{speller}}'
        },
        'PersistentDictionary': {
            'fabric': 'modules.services.db.shelve_dict_fabric.ShelveDictFabric',
            'config': {
                'file': '{{app.lib}}/dict.db'
            }
        },
        'Statistics': {
            'fabric': 'modules.services.statistics.fabric.StatisticsFabric',
            'config': {
                'file': '/home/devel/statistics.db'
            }
        },
        'SendMail': {
            'fabric': 'modules.services.sendmail.postfix_sendmail_fabric.PostfixSendMailFabric',
            'config': {
                'bin': '/usr/sbin/sendmail',
                'args': ['-G', '-i', '-f']
            }
        }
    },
    'speller': {},
    'modules': {
        'stages': {
            'chain': 'modules.pipeline.stages.chain.Chain',
            'disclaimer': 'modules.pipeline.stages.disclaimer.Disclaimer',
            'dkim': 'modules.pipeline.stages.dkim.DKIM',
            'remove_hashtag': 'modules.pipeline.stages.remove_hashtag.RemoveHashTag',
            'logo_inject': 'modules.pipeline.stages.logo_inject.LogoInject',
            'vcard_inject': 'modules.pipeline.stages.vcard_inject.VcardInject',
            'isolator': 'modules.pipeline.stages.isolator.Isolator',
            'beautifulizer': 'modules.pipeline.stages.beautifulizer.Beautifulizer',
            'statistics_feeder': 'modules.pipeline.stages.statistics_feeder.StatisticsFeeder',
            'copy': 'modules.pipeline.stages.copy.Copy',
            'switch': 'modules.pipeline.stages.switch.Switch',
            'break': 'modules.pipeline.stages.break.Break',
            'header': 'modules.pipeline.stages.header_inject.HeaderInject',
            'bus_interact': 'modules.pipeline.stages.bus_interact.BusInteract'
        },
        'filters': {
            'attrib': 'modules.pipeline.filters.attributes.Attributes',
            'auth': 'modules.pipeline.filters.auth.Auth',
            'pass': 'modules.pipeline.filters.bypass.Bypass',
            'expr': 'modules.pipeline.filters.expression.Expression',
            'filter': 'modules.pipeline.filters.aggregation.Aggregation',
            'hashtag': 'modules.pipeline.filters.hashtag.HashTag',
            'statistics': 'modules.pipeline.filters.statistics.Statistics',
            'header': 'modules.pipeline.filters.header.Header',
            'stage': 'modules.pipeline.filters.stage.Stage'
        }
    },
    'app': {
        'full_name': 'QueueMagic',
        'description': 'SMTP content filter and processor',
        'test': '{{app.full_name}} the {{app.description}}',
        'name': 'queuemagic',
        'sh_name': 'qm',
        'spool': '/var/spool/{{app.name}}',
        'lib': '/var/lib/{{app.name}}',
        'cache': '{{app.lib}}/cache',
        'storage': {
            'directory': '{{app.spool}}/tmp',
            'prefix': '{{app.sh_name}}',
            'suffix': 'tmp'
        }
    },
    'env': {
        'dialog_antiquity': 60 * 60 * 24 * 7  # 1 week
    }
}