#!/usr/bin/env python3
"""Rebuild chat widget: interactive option buttons instead of contact-info responses.
Also update Telegram notification format."""

import os
import glob
import re

BASE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')

# ── CSS to add for chat option buttons ──
CHAT_BTN_CSS = """
        .chat-options {
            display: flex;
            flex-wrap: wrap;
            gap: 6px;
            margin-top: 8px;
            padding-left: 36px;
        }

        .chat-opt-btn {
            background: #fff;
            color: #001D4A;
            border: 1.5px solid #006992;
            border-radius: 20px;
            padding: 5px 14px;
            font-size: 0.72rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.15s;
            font-family: inherit;
            white-space: nowrap;
        }

        .chat-opt-btn:hover {
            background: #006992;
            color: #fff;
        }

        .chat-opt-btn.amber {
            border-color: #ECA400;
            background: #ECA400;
            color: #001D4A;
        }

        .chat-opt-btn.amber:hover {
            background: #d4940a;
        }

"""

# ── OLD JS block to replace (from chatResponses to end of chat) ──
OLD_JS_START = "            var chatResponses = {"
OLD_JS_END = """            document.addEventListener('click', function(e) {
                if (!chatWidget2.contains(e.target) && chatWidget2.classList.contains('open')) {
                    chatWidget2.classList.remove('open');
                }
            });
        }"""

NEW_CHAT_JS = """            // -- Chat bot conversation flow --
            var chatStep = 'start';
            var chatData = {};

            function chatAddMsg(text, isSent) {
                var msg = document.createElement('div');
                msg.className = 'chat-msg' + (isSent ? ' sent' : '');
                msg.innerHTML = '<div class="chat-msg-avatar">' + (isSent ? 'You' : 'BB') + '</div><div class="chat-msg-bubble">' + text + '</div>';
                chatBody2.appendChild(msg);
                chatBody2.scrollTop = chatBody2.scrollHeight;
            }

            function chatAddOptions(options) {
                var wrap = document.createElement('div');
                wrap.className = 'chat-options';
                options.forEach(function(opt) {
                    var btn = document.createElement('button');
                    btn.className = 'chat-opt-btn' + (opt.amber ? ' amber' : '');
                    btn.textContent = opt.label;
                    btn.addEventListener('click', function() {
                        // Remove all option buttons
                        var allOpts = chatBody2.querySelectorAll('.chat-options');
                        allOpts.forEach(function(o) { o.remove(); });
                        chatAddMsg(opt.label, true);
                        // Notify backend
                        chatNotify(opt.label);
                        setTimeout(function() { opt.action(); }, 400);
                    });
                    wrap.appendChild(btn);
                });
                chatBody2.appendChild(wrap);
                chatBody2.scrollTop = chatBody2.scrollHeight;
            }

            function chatAddLoading() {
                var loader = document.createElement('div');
                loader.className = 'chat-msg';
                loader.id = 'chatLoader';
                loader.innerHTML = '<div class="chat-msg-avatar">BB</div><div class="chat-loading"><span></span><span></span><span></span></div>';
                chatBody2.appendChild(loader);
                chatBody2.scrollTop = chatBody2.scrollHeight;
            }

            function chatRemoveLoading() {
                var loader = document.getElementById('chatLoader');
                if (loader) loader.remove();
            }

            function chatNotify(text) {
                try {
                    fetch('/api/chat', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            message: text,
                            page: window.location.pathname,
                            timestamp: new Date().toLocaleString('en-US', { timeZone: 'America/New_York' }),
                            step: chatStep,
                            data: chatData
                        })
                    }).catch(function() {});
                } catch(e) {}
            }

            function chatShowMainMenu() {
                chatStep = 'main_menu';
                chatAddMsg("How can I help you today?");
                chatAddOptions([
                    { label: 'Get a Quote', amber: true, action: chatFlowQuoteStart },
                    { label: 'Our Services', action: chatFlowServices },
                    { label: 'Service Areas', action: chatFlowAreas },
                    { label: 'Book a Cleaning', amber: true, action: chatFlowBook },
                    { label: 'Talk to Someone', action: chatFlowHuman }
                ]);
            }

            // ── QUOTE FLOW ──
            function chatFlowQuoteStart() {
                chatStep = 'quote_type';
                chatAddMsg("What type of cleaning do you need?");
                chatAddOptions([
                    { label: 'Deep Cleaning', action: function() { chatData.service = 'Deep Cleaning'; chatFlowQuoteSize(); }},
                    { label: 'Post-Construction', action: function() { chatData.service = 'Post-Construction'; chatFlowQuoteSize(); }},
                    { label: 'Move-In / Move-Out', action: function() { chatData.service = 'Move-In / Move-Out'; chatFlowQuoteSize(); }},
                    { label: 'Recurring Cleaning', action: function() { chatData.service = 'Recurring Cleaning'; chatFlowQuoteSize(); }},
                    { label: 'Commercial / Office', action: function() { chatData.service = 'Commercial / Office'; chatFlowQuoteSize(); }},
                    { label: 'Other', action: function() { chatData.service = 'Other'; chatFlowQuoteSize(); }}
                ]);
            }

            function chatFlowQuoteSize() {
                chatStep = 'quote_size';
                chatAddMsg("What\\'s the approximate size?");
                chatAddOptions([
                    { label: 'Studio / 1 BR', action: function() { chatData.size = 'Studio/1BR'; chatFlowQuoteContact(); }},
                    { label: '2-3 Bedrooms', action: function() { chatData.size = '2-3BR'; chatFlowQuoteContact(); }},
                    { label: '4+ Bedrooms', action: function() { chatData.size = '4+BR'; chatFlowQuoteContact(); }},
                    { label: 'Office / Commercial', action: function() { chatData.size = 'Commercial'; chatFlowQuoteContact(); }},
                    { label: 'Not Sure', action: function() { chatData.size = 'Unknown'; chatFlowQuoteContact(); }}
                ]);
            }

            function chatFlowQuoteContact() {
                chatStep = 'quote_contact';
                chatAddMsg("Got it — <strong>" + chatData.service + "</strong> for a <strong>" + chatData.size + "</strong> space. How should we send your quote?");
                chatAddOptions([
                    { label: 'Text Me', amber: true, action: chatFlowAskPhone },
                    { label: 'Email Me', amber: true, action: chatFlowAskEmail },
                    { label: 'Use Quote Calculator', action: function() {
                        chatAddMsg("<a href=\\'/tools/quote-calculator.html\\' target=\\'_blank\\' style=\\'color:#ECA400;font-weight:700\\'>Open Quote Calculator →</a>");
                        setTimeout(chatFlowAnythingElse, 1500);
                    }}
                ]);
            }

            function chatFlowAskPhone() {
                chatStep = 'collect_phone';
                chatAddMsg("What\\'s your phone number? We\\'ll text you a quote within 2 hours.");
                chatData.contactMethod = 'phone';
            }

            function chatFlowAskEmail() {
                chatStep = 'collect_email';
                chatAddMsg("What\\'s your email? We\\'ll send your quote within 2 hours.");
                chatData.contactMethod = 'email';
            }

            function chatFlowCollectContact(text) {
                chatData.contact = text;
                chatStep = 'quote_done';
                chatAddMsg("Thanks! We\\'ll reach out shortly with your <strong>" + chatData.service + "</strong> quote. Expect to hear from us within 2 hours.");
                setTimeout(chatFlowAnythingElse, 2000);
            }

            // ── SERVICES FLOW ──
            function chatFlowServices() {
                chatStep = 'services';
                chatAddMsg("Here\\'s what we offer:");
                chatAddOptions([
                    { label: 'Deep Cleaning', action: function() { chatAddMsg("Top-to-bottom deep cleaning for homes — kitchens, bathrooms, baseboards, appliances, everything."); setTimeout(chatFlowAnythingElse, 1500); }},
                    { label: 'Post-Construction', action: function() { chatAddMsg("Dust, debris & residue removal after renovations. We make new builds move-in ready."); setTimeout(chatFlowAnythingElse, 1500); }},
                    { label: 'Move-In / Move-Out', action: function() { chatAddMsg("Get your full deposit back or start fresh in your new place. Every surface cleaned."); setTimeout(chatFlowAnythingElse, 1500); }},
                    { label: 'Commercial Cleaning', action: function() { chatAddMsg("Office, retail & commercial spaces. Flexible scheduling, consistent results."); setTimeout(chatFlowAnythingElse, 1500); }},
                    { label: 'Spring Cleaning', action: function() { chatAddMsg("Seasonal refresh — windows, deep scrub, organize. Start the season right."); setTimeout(chatFlowAnythingElse, 1500); }},
                    { label: 'Get a Quote', amber: true, action: chatFlowQuoteStart }
                ]);
            }

            // ── AREAS FLOW ──
            function chatFlowAreas() {
                chatStep = 'areas';
                chatAddMsg("We serve <strong>15 cities</strong> across Greater Boston: Boston, Cambridge, Newton, Waltham, Brookline, Somerville, Brighton, Watertown, Allston, East Boston, South Boston, Lexington, Needham, Wellesley & Weston.");
                chatAddOptions([
                    { label: 'Get a Quote', amber: true, action: chatFlowQuoteStart },
                    { label: 'View All Areas', action: function() { window.open('/cities.html', '_blank'); }},
                    { label: 'Back to Menu', action: chatShowMainMenu }
                ]);
            }

            // ── BOOK FLOW ──
            function chatFlowBook() {
                chatStep = 'book';
                chatAddMsg("Let\\'s get you booked! First, what service do you need?");
                chatAddOptions([
                    { label: 'Deep Cleaning', action: function() { chatData.service = 'Deep Cleaning'; chatFlowBookContact(); }},
                    { label: 'Post-Construction', action: function() { chatData.service = 'Post-Construction'; chatFlowBookContact(); }},
                    { label: 'Move-In / Move-Out', action: function() { chatData.service = 'Move-In / Move-Out'; chatFlowBookContact(); }},
                    { label: 'Other', action: function() { chatData.service = 'Other'; chatFlowBookContact(); }}
                ]);
            }

            function chatFlowBookContact() {
                chatStep = 'book_contact';
                chatAddMsg("Great choice! How should we reach you to schedule?");
                chatAddOptions([
                    { label: 'Text Me', amber: true, action: chatFlowAskPhone },
                    { label: 'Email Me', amber: true, action: chatFlowAskEmail }
                ]);
            }

            // ── TALK TO HUMAN ──
            function chatFlowHuman() {
                chatStep = 'human';
                chatAddMsg("We\\'d love to help personally! Fastest way to reach us:");
                chatAddOptions([
                    { label: 'Text (781) 330-5604', amber: true, action: function() { window.open('sms:+17813305604', '_self'); }},
                    { label: 'Email Us', action: function() { window.open('mailto:bluebrickmass@gmail.com', '_self'); }},
                    { label: 'Back to Menu', action: chatShowMainMenu }
                ]);
            }

            // ── ANYTHING ELSE ──
            function chatFlowAnythingElse() {
                chatAddMsg("Anything else I can help with?");
                chatAddOptions([
                    { label: 'Get a Quote', amber: true, action: chatFlowQuoteStart },
                    { label: 'Our Services', action: chatFlowServices },
                    { label: 'Talk to Someone', action: chatFlowHuman },
                    { label: "I'm Good!", action: function() { chatAddMsg("Thanks for chatting! We\\'re here anytime you need us. 👋"); }}
                ]);
            }

            // ── HANDLE FREE TEXT INPUT ──
            function chatHandleSend() {
                var text = chatInput2.value.trim();
                if (!text) return;
                chatAddMsg(text, true);
                chatInput2.value = '';

                // Notify backend
                chatNotify(text);

                // If we're collecting contact info, capture it
                if (chatStep === 'collect_phone' || chatStep === 'collect_email') {
                    chatAddLoading();
                    setTimeout(function() {
                        chatRemoveLoading();
                        chatFlowCollectContact(text);
                    }, 600);
                    return;
                }

                // Otherwise, smart reply based on keywords
                chatAddLoading();
                setTimeout(function() {
                    chatRemoveLoading();
                    var t = text.toLowerCase();
                    if (t.indexOf('quote') > -1 || t.indexOf('estimate') > -1 || t.indexOf('cost') > -1 || t.indexOf('price') > -1 || t.indexOf('how much') > -1) {
                        chatFlowQuoteStart();
                    } else if (t.indexOf('service') > -1 || t.indexOf('offer') > -1 || t.indexOf('clean') > -1) {
                        chatFlowServices();
                    } else if (t.indexOf('area') > -1 || t.indexOf('city') > -1 || t.indexOf('where') > -1) {
                        chatFlowAreas();
                    } else if (t.indexOf('book') > -1 || t.indexOf('schedule') > -1) {
                        chatFlowBook();
                    } else if (t.indexOf('talk') > -1 || t.indexOf('human') > -1 || t.indexOf('person') > -1 || t.indexOf('call') > -1) {
                        chatFlowHuman();
                    } else {
                        chatAddMsg("Thanks for your message! Let me help you find what you need.");
                        chatAddOptions([
                            { label: 'Get a Quote', amber: true, action: chatFlowQuoteStart },
                            { label: 'Our Services', action: chatFlowServices },
                            { label: 'Service Areas', action: chatFlowAreas },
                            { label: 'Talk to Someone', action: chatFlowHuman }
                        ]);
                    }
                }, 600);
            }

            chatSendBtn2.addEventListener('click', chatHandleSend);
            chatInput2.addEventListener('keydown', function(e) {
                if (e.key === 'Enter') { e.preventDefault(); chatHandleSend(); }
            });

            // Quick action buttons trigger main flows
            document.querySelectorAll('.chat-quick-btn').forEach(function(btn) {
                btn.addEventListener('click', function() {
                    var msg = btn.getAttribute('data-msg');
                    chatAddMsg(msg, true);
                    chatNotify(msg);
                    // Remove all option buttons first
                    var allOpts = chatBody2.querySelectorAll('.chat-options');
                    allOpts.forEach(function(o) { o.remove(); });
                    if (msg.indexOf('quote') > -1 || msg.indexOf('Quote') > -1) chatFlowQuoteStart();
                    else if (msg.indexOf('service') > -1 || msg.indexOf('Service') > -1) chatFlowServices();
                    else if (msg.indexOf('area') > -1 || msg.indexOf('Area') > -1) chatFlowAreas();
                    else chatShowMainMenu();
                });
            });

            document.addEventListener('click', function(e) {
                if (!chatWidget2.contains(e.target) && chatWidget2.classList.contains('open')) {
                    chatWidget2.classList.remove('open');
                }
            });
        }"""


def process_file(filepath):
    with open(filepath, 'r') as f:
        content = f.read()

    original = content
    basename = os.path.basename(filepath)
    changes = []

    # 1. Add chat option button CSS
    if '.chat-opt-btn' not in content:
        marker = '        .chat-quick-btn {'
        if marker in content:
            idx = content.find(marker)
            content = content[:idx] + CHAT_BTN_CSS + content[idx:]
            changes.append('css')

    # 2. Replace chat JS
    start_idx = content.find(OLD_JS_START)
    end_marker = OLD_JS_END
    end_idx = content.find(end_marker)

    if start_idx != -1 and end_idx != -1:
        end_idx += len(end_marker)
        content = content[:start_idx] + NEW_CHAT_JS + content[end_idx:]
        changes.append('js')

    if content != original:
        with open(filepath, 'w') as f:
            f.write(content)
        print(f'  OK [{", ".join(changes)}]: {basename}')
        return True
    else:
        print(f'  SKIP: {basename}')
        return False


def main():
    files = sorted(glob.glob(os.path.join(BASE_DIR, 'blog', '*.html')))
    for name in ['index.html', 'cities.html']:
        files.append(os.path.join(BASE_DIR, name))
    files.append(os.path.join(BASE_DIR, 'tools', 'quote-calculator.html'))

    updated = 0
    for f in files:
        if not os.path.exists(f):
            continue
        if process_file(f):
            updated += 1

    print(f'\nUpdated {updated} files')


if __name__ == '__main__':
    main()
