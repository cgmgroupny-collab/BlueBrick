#!/usr/bin/env python3
"""
Add vanilla HTML/CSS/JS versions of:
1. Expandable chat widget (bottom-right, replaces floating CTA)
2. Tubelight animated navbar (replaces current header nav)
Both adapted from React/shadcn components into pure CSS/JS.
"""

import os
import re
import glob

BLOG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'blog')

# ─────────────────────────────────────────────
# 1. EXPANDABLE CHAT WIDGET CSS
# ─────────────────────────────────────────────
CHAT_CSS = """
        /* ============================================
           EXPANDABLE CHAT WIDGET
           ============================================ */
        .chat-widget {
            position: fixed;
            bottom: 1.5rem;
            right: 1.5rem;
            z-index: 1000;
            font-family: var(--font-body, 'Manrope', sans-serif);
        }

        .chat-toggle {
            width: 56px;
            height: 56px;
            border-radius: 50%;
            border: none;
            background: linear-gradient(135deg, #006992, #004f6e);
            color: #fff;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            box-shadow: 0 4px 20px rgba(0, 105, 146, 0.4), 0 0 0 0 rgba(0, 105, 146, 0.3);
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            position: relative;
            z-index: 2;
        }

        .chat-toggle::after {
            content: '';
            position: absolute;
            inset: -5px;
            border-radius: 50%;
            background: rgba(0, 105, 146, 0.2);
            animation: chatPulse 2.5s ease-in-out infinite;
            z-index: -1;
        }

        @keyframes chatPulse {
            0%, 100% { transform: scale(1); opacity: 0.4; }
            50% { transform: scale(1.3); opacity: 0; }
        }

        .chat-widget.open .chat-toggle::after { animation: none; opacity: 0; }

        .chat-toggle:hover {
            transform: scale(1.08);
            box-shadow: 0 6px 28px rgba(0, 105, 146, 0.5);
        }

        .chat-toggle svg {
            width: 24px;
            height: 24px;
            fill: none;
            stroke: #fff;
            stroke-width: 2;
            stroke-linecap: round;
            stroke-linejoin: round;
            transition: transform 0.3s;
        }

        .chat-toggle .icon-close { display: none; }
        .chat-widget.open .chat-toggle .icon-chat { display: none; }
        .chat-widget.open .chat-toggle .icon-close { display: block; }

        .chat-panel {
            position: absolute;
            bottom: calc(100% + 12px);
            right: 0;
            width: 370px;
            max-height: 520px;
            background: #fff;
            border-radius: 16px;
            box-shadow: 0 12px 48px rgba(0, 0, 0, 0.15), 0 0 0 1px rgba(0, 0, 0, 0.05);
            display: flex;
            flex-direction: column;
            overflow: hidden;
            opacity: 0;
            visibility: hidden;
            transform: translateY(12px) scale(0.95);
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }

        .chat-widget.open .chat-panel {
            opacity: 1;
            visibility: visible;
            transform: translateY(0) scale(1);
        }

        .chat-panel-header {
            padding: 1.25rem 1.25rem 1rem;
            background: linear-gradient(135deg, #001D4A, #0a2a5c);
            color: #fff;
            text-align: center;
        }

        .chat-panel-header h3 {
            font-family: var(--font-display, 'Bebas Neue', sans-serif);
            font-size: 1.15rem;
            font-weight: 400;
            letter-spacing: 0.04em;
            margin: 0 0 0.2rem;
        }

        .chat-panel-header p {
            font-size: 0.75rem;
            color: rgba(255, 255, 255, 0.65);
            margin: 0;
        }

        .chat-panel-body {
            flex: 1;
            padding: 1rem 1rem 0.5rem;
            overflow-y: auto;
            display: flex;
            flex-direction: column;
            gap: 0.75rem;
            max-height: 300px;
            background: #f9fafb;
        }

        .chat-msg {
            display: flex;
            gap: 0.5rem;
            align-items: flex-end;
            animation: chatMsgIn 0.3s ease-out;
        }

        @keyframes chatMsgIn {
            from { opacity: 0; transform: translateY(8px); }
            to { opacity: 1; transform: translateY(0); }
        }

        .chat-msg.sent { flex-direction: row-reverse; }

        .chat-msg-avatar {
            width: 30px;
            height: 30px;
            border-radius: 50%;
            background: linear-gradient(135deg, #006992, #004f6e);
            display: flex;
            align-items: center;
            justify-content: center;
            flex-shrink: 0;
            font-size: 0.6rem;
            color: #fff;
            font-weight: 700;
        }

        .chat-msg.sent .chat-msg-avatar {
            background: linear-gradient(135deg, #ECA400, #d4940a);
            color: #001D4A;
        }

        .chat-msg-bubble {
            padding: 0.6rem 0.85rem;
            border-radius: 12px;
            font-size: 0.82rem;
            line-height: 1.5;
            max-width: 75%;
        }

        .chat-msg:not(.sent) .chat-msg-bubble {
            background: #fff;
            color: #374151;
            border: 1px solid #e5e7eb;
            border-bottom-left-radius: 4px;
        }

        .chat-msg.sent .chat-msg-bubble {
            background: linear-gradient(135deg, #006992, #005577);
            color: #fff;
            border-bottom-right-radius: 4px;
        }

        .chat-loading {
            display: flex;
            gap: 4px;
            padding: 0.6rem 0.85rem;
        }

        .chat-loading span {
            width: 6px;
            height: 6px;
            border-radius: 50%;
            background: #9ca3af;
            animation: chatDot 1.2s ease-in-out infinite;
        }

        .chat-loading span:nth-child(2) { animation-delay: 0.15s; }
        .chat-loading span:nth-child(3) { animation-delay: 0.3s; }

        @keyframes chatDot {
            0%, 100% { transform: translateY(0); }
            50% { transform: translateY(-5px); }
        }

        .chat-panel-footer {
            padding: 0.75rem;
            border-top: 1px solid #e5e7eb;
            background: #fff;
        }

        .chat-input-wrap {
            display: flex;
            gap: 0.5rem;
            align-items: center;
            background: #f9fafb;
            border: 1px solid #e5e7eb;
            border-radius: 10px;
            padding: 0.35rem 0.5rem 0.35rem 0.85rem;
            transition: border-color 0.2s;
        }

        .chat-input-wrap:focus-within {
            border-color: #006992;
        }

        .chat-input-wrap input {
            flex: 1;
            border: none;
            background: none;
            font-size: 0.82rem;
            font-family: inherit;
            color: #374151;
            outline: none;
        }

        .chat-input-wrap input::placeholder { color: #9ca3af; }

        .chat-send-btn {
            width: 32px;
            height: 32px;
            border-radius: 8px;
            border: none;
            background: linear-gradient(135deg, #006992, #005577);
            color: #fff;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: all 0.2s;
            flex-shrink: 0;
        }

        .chat-send-btn:hover {
            background: linear-gradient(135deg, #007ba8, #006992);
            transform: scale(1.05);
        }

        .chat-send-btn svg {
            width: 16px;
            height: 16px;
            fill: none;
            stroke: #fff;
            stroke-width: 2;
            stroke-linecap: round;
            stroke-linejoin: round;
        }

        .chat-quick-actions {
            display: flex;
            gap: 0.35rem;
            margin-top: 0.5rem;
            flex-wrap: wrap;
        }

        .chat-quick-btn {
            font-size: 0.7rem;
            padding: 0.3rem 0.65rem;
            border-radius: 20px;
            border: 1px solid #e5e7eb;
            background: #fff;
            color: #374151;
            cursor: pointer;
            font-family: inherit;
            transition: all 0.2s;
        }

        .chat-quick-btn:hover {
            border-color: #006992;
            color: #006992;
            background: rgba(0, 105, 146, 0.04);
        }

        @media (max-width: 480px) {
            .chat-panel {
                position: fixed;
                inset: 0;
                width: 100%;
                max-height: 100%;
                border-radius: 0;
                bottom: 0;
                right: 0;
            }

            .chat-panel-body { max-height: calc(100vh - 200px); }

            .chat-widget.open .chat-toggle {
                position: fixed;
                top: 1rem;
                right: 1rem;
                bottom: auto;
                z-index: 1001;
            }
        }"""

# ─────────────────────────────────────────────
# 2. TUBELIGHT NAVBAR CSS
# ─────────────────────────────────────────────
NAVBAR_CSS = """
        /* ============================================
           TUBELIGHT NAVBAR
           ============================================ */
        .tube-nav {
            position: fixed;
            top: 0;
            left: 50%;
            transform: translateX(-50%);
            z-index: 1001;
            padding-top: 1rem;
            pointer-events: none;
            transition: opacity 0.4s;
        }

        .tube-nav-inner {
            display: flex;
            align-items: center;
            gap: 0.25rem;
            background: rgba(0, 29, 74, 0.08);
            border: 1px solid rgba(0, 29, 74, 0.1);
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
            padding: 0.3rem;
            border-radius: 999px;
            box-shadow: 0 4px 24px rgba(0, 0, 0, 0.08);
            pointer-events: all;
        }

        .tube-nav.scrolled .tube-nav-inner {
            background: rgba(255, 255, 255, 0.92);
            border-color: rgba(0, 29, 74, 0.08);
            box-shadow: 0 4px 30px rgba(0, 0, 0, 0.1);
        }

        .tube-nav-link {
            position: relative;
            font-size: 0.72rem;
            font-weight: 600;
            letter-spacing: 0.06em;
            text-transform: uppercase;
            padding: 0.5rem 1.1rem;
            border-radius: 999px;
            color: rgba(255, 255, 255, 0.85) !important;
            text-decoration: none !important;
            white-space: nowrap;
            transition: color 0.3s, background 0.3s;
        }

        .tube-nav.scrolled .tube-nav-link {
            color: var(--prussian, #001D4A) !important;
        }

        .tube-nav-link:hover {
            color: #ECA400 !important;
        }

        .tube-nav-link.active {
            color: #ECA400 !important;
            background: rgba(236, 164, 0, 0.08);
        }

        /* The tubelight glow */
        .tube-nav-link.active::before {
            content: '';
            position: absolute;
            top: -2px;
            left: 50%;
            transform: translateX(-50%);
            width: 28px;
            height: 3px;
            background: #ECA400;
            border-radius: 3px 3px 0 0;
        }

        .tube-nav-link.active::after {
            content: '';
            position: absolute;
            top: -6px;
            left: 50%;
            transform: translateX(-50%);
            width: 40px;
            height: 16px;
            background: radial-gradient(ellipse, rgba(236, 164, 0, 0.25), transparent 70%);
            filter: blur(4px);
            pointer-events: none;
        }

        .tube-nav-cta {
            padding: 0.5rem 1.2rem !important;
            background: linear-gradient(135deg, #ECA400, #d4940a) !important;
            color: #001D4A !important;
            font-weight: 700 !important;
            box-shadow: 0 2px 10px rgba(236, 164, 0, 0.3);
            transition: all 0.3s !important;
        }

        .tube-nav-cta:hover {
            transform: translateY(-1px);
            box-shadow: 0 4px 16px rgba(236, 164, 0, 0.4) !important;
            color: #001D4A !important;
        }

        .tube-nav-logo {
            display: flex;
            align-items: center;
            padding: 0.25rem 0.75rem 0.25rem 0.5rem;
            text-decoration: none !important;
        }

        .tube-nav-logo img {
            height: 26px;
            width: auto;
            filter: brightness(0) invert(1);
            transition: filter 0.3s;
        }

        .tube-nav.scrolled .tube-nav-logo img {
            filter: none;
        }

        /* Mobile: icon-only nav */
        .tube-nav-link .nav-icon { display: none; }
        .tube-nav-link .nav-label { display: inline; }

        @media (max-width: 768px) {
            .tube-nav {
                top: auto;
                bottom: 0;
                padding-top: 0;
                padding-bottom: 0.75rem;
                width: 100%;
                display: flex;
                justify-content: center;
            }

            .tube-nav-inner {
                gap: 0.15rem;
                padding: 0.25rem;
            }

            .tube-nav-link .nav-label { display: none; }
            .tube-nav-link .nav-icon { display: flex; }
            .tube-nav-link { padding: 0.55rem 0.85rem; }

            .tube-nav-logo { display: none; }

            .tube-nav-cta .nav-label { display: none; }
            .tube-nav-cta .nav-icon { display: flex; }

            /* Adjust other fixed elements */
            .contact-fab { bottom: 5rem !important; }
            .back-to-top { bottom: 5rem !important; }
        }"""


# ─────────────────────────────────────────────
# 3. CHAT WIDGET HTML
# ─────────────────────────────────────────────
CHAT_HTML = """
    <!-- Expandable Chat Widget -->
    <div class="chat-widget" id="chatWidget">
        <div class="chat-panel">
            <div class="chat-panel-header">
                <h3>BLUE BRICK CONCIERGE</h3>
                <p>We typically reply in minutes</p>
            </div>
            <div class="chat-panel-body" id="chatBody">
                <div class="chat-msg">
                    <div class="chat-msg-avatar">BB</div>
                    <div class="chat-msg-bubble">Hi there! Looking for a cleaning quote? I can help you get started.</div>
                </div>
            </div>
            <div class="chat-panel-footer">
                <div class="chat-input-wrap">
                    <input type="text" id="chatInput" placeholder="Type a message..." autocomplete="off">
                    <button class="chat-send-btn" id="chatSendBtn" aria-label="Send">
                        <svg viewBox="0 0 24 24"><line x1="22" y1="2" x2="11" y2="13"/><polygon points="22 2 15 22 11 13 2 9 22 2"/></svg>
                    </button>
                </div>
                <div class="chat-quick-actions">
                    <button class="chat-quick-btn" data-msg="I need a quote">Get a Quote</button>
                    <button class="chat-quick-btn" data-msg="What services do you offer?">Services</button>
                    <button class="chat-quick-btn" data-msg="What areas do you cover?">Service Areas</button>
                </div>
            </div>
        </div>
        <button class="chat-toggle" id="chatToggle" aria-label="Open chat">
            <svg class="icon-chat" viewBox="0 0 24 24"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>
            <svg class="icon-close" viewBox="0 0 24 24"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
        </button>
    </div>
"""

# ─────────────────────────────────────────────
# 4. TUBELIGHT NAVBAR HTML (replaces old <header>)
# ─────────────────────────────────────────────
NAVBAR_HTML = """    <div class="tube-nav" id="tubeNav">
        <div class="tube-nav-inner">
            <a href="/" class="tube-nav-logo" aria-label="Blue Brick Home">
                <img src="../assets/images/IMG_9670.png" alt="Blue Brick">
            </a>
            <a href="/#services" class="tube-nav-link">
                <span class="nav-label">Services</span>
                <span class="nav-icon"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z"/></svg></span>
            </a>
            <a href="/cities.html" class="tube-nav-link">
                <span class="nav-label">Areas</span>
                <span class="nav-icon"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/><circle cx="12" cy="10" r="3"/></svg></span>
            </a>
            <a href="/blog/" class="tube-nav-link active">
                <span class="nav-label">Blog</span>
                <span class="nav-icon"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/></svg></span>
            </a>
            <a href="sms:+17813305604" class="tube-nav-link">
                <span class="nav-label">Text Us</span>
                <span class="nav-icon"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg></span>
            </a>
            <a href="/#quote" class="tube-nav-link tube-nav-cta">
                <span class="nav-label">Free Estimate</span>
                <span class="nav-icon"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 12 20 22 4 22 4 12"/><rect x="2" y="7" width="20" height="5"/><line x1="12" y1="22" x2="12" y2="7"/><path d="M12 7H7.5a2.5 2.5 0 0 1 0-5C11 2 12 7 12 7z"/><path d="M12 7h4.5a2.5 2.5 0 0 0 0-5C13 2 12 7 12 7z"/></svg></span>
            </a>
        </div>
    </div>
"""

# ─────────────────────────────────────────────
# 5. CHAT WIDGET JS
# ─────────────────────────────────────────────
CHAT_JS = """
        // -- Expandable Chat Widget --
        const chatWidget = document.getElementById('chatWidget');
        const chatToggle = document.getElementById('chatToggle');
        const chatInput = document.getElementById('chatInput');
        const chatSendBtn = document.getElementById('chatSendBtn');
        const chatBody = document.getElementById('chatBody');

        if (chatToggle) {
            chatToggle.addEventListener('click', () => {
                chatWidget.classList.toggle('open');
                if (chatWidget.classList.contains('open')) {
                    setTimeout(() => chatInput.focus(), 300);
                }
            });

            // Auto-responses
            const responses = {
                'quote': "Great! For a quick estimate, try our <a href='/tools/quote-calculator.html' target='_blank' style='color:#ECA400;font-weight:600'>Quote Calculator</a> or text us at <a href='sms:+17813305604' style='color:#ECA400;font-weight:600'>(781) 330-5604</a> with your address and sqft!",
                'services': "We offer: Deep Cleaning, Post-Construction Cleanup, Move-In/Move-Out, Luxury Residential, Commercial Cleaning, and Spring Cleaning. Which interests you?",
                'areas': "We serve 15 cities: Boston, Cambridge, Newton, Waltham, Brookline, Somerville, Brighton, Watertown, Allston, East Boston, South Boston, Lexington, Needham, Wellesley, and Weston!",
                'price': "Pricing depends on square footage and service type. Use our <a href='/tools/quote-calculator.html' target='_blank' style='color:#ECA400;font-weight:600'>Quote Calculator</a> for an instant estimate!",
                'book': "To book, text us at <a href='sms:+17813305604' style='color:#ECA400;font-weight:600'>(781) 330-5604</a> or email <a href='mailto:bluebrickmass@gmail.com' style='color:#ECA400;font-weight:600'>bluebrickmass@gmail.com</a>. We respond within 2 hours!",
                'default': "Thanks for your message! For the fastest response, text us at <a href='sms:+17813305604' style='color:#ECA400;font-weight:600'>(781) 330-5604</a> or email <a href='mailto:bluebrickmass@gmail.com' style='color:#ECA400;font-weight:600'>bluebrickmass@gmail.com</a>."
            };

            function addMessage(text, isSent) {
                const msg = document.createElement('div');
                msg.className = 'chat-msg' + (isSent ? ' sent' : '');
                msg.innerHTML = '<div class="chat-msg-avatar">' + (isSent ? 'You' : 'BB') + '</div><div class="chat-msg-bubble">' + text + '</div>';
                chatBody.appendChild(msg);
                chatBody.scrollTop = chatBody.scrollHeight;
            }

            function addLoading() {
                const loader = document.createElement('div');
                loader.className = 'chat-msg';
                loader.id = 'chatLoader';
                loader.innerHTML = '<div class="chat-msg-avatar">BB</div><div class="chat-loading"><span></span><span></span><span></span></div>';
                chatBody.appendChild(loader);
                chatBody.scrollTop = chatBody.scrollHeight;
            }

            function removeLoading() {
                const loader = document.getElementById('chatLoader');
                if (loader) loader.remove();
            }

            function getResponse(text) {
                const t = text.toLowerCase();
                if (t.includes('quote') || t.includes('estimate') || t.includes('cost') || t.includes('pricing')) return responses.quote;
                if (t.includes('service') || t.includes('offer') || t.includes('clean')) return responses.services;
                if (t.includes('area') || t.includes('city') || t.includes('cities') || t.includes('where') || t.includes('cover') || t.includes('location')) return responses.areas;
                if (t.includes('price') || t.includes('how much') || t.includes('rate')) return responses.price;
                if (t.includes('book') || t.includes('schedule') || t.includes('appointment')) return responses.book;
                return responses.default;
            }

            function handleSend() {
                const text = chatInput.value.trim();
                if (!text) return;
                addMessage(text, true);
                chatInput.value = '';
                addLoading();
                setTimeout(() => {
                    removeLoading();
                    addMessage(getResponse(text), false);
                }, 800 + Math.random() * 600);
            }

            chatSendBtn.addEventListener('click', handleSend);
            chatInput.addEventListener('keydown', (e) => {
                if (e.key === 'Enter') { e.preventDefault(); handleSend(); }
            });

            document.querySelectorAll('.chat-quick-btn').forEach(btn => {
                btn.addEventListener('click', () => {
                    const msg = btn.getAttribute('data-msg');
                    chatInput.value = msg;
                    handleSend();
                });
            });

            // Close on outside click
            document.addEventListener('click', (e) => {
                if (!chatWidget.contains(e.target) && chatWidget.classList.contains('open')) {
                    chatWidget.classList.remove('open');
                }
            });
        }"""

# ─────────────────────────────────────────────
# 6. TUBELIGHT NAVBAR JS
# ─────────────────────────────────────────────
NAVBAR_JS = """
        // -- Tubelight Navbar --
        const tubeNav = document.getElementById('tubeNav');
        if (tubeNav) {
            window.addEventListener('scroll', () => {
                if (window.scrollY > 100) {
                    tubeNav.classList.add('scrolled');
                } else {
                    tubeNav.classList.remove('scrolled');
                }
            });

            // Set active link based on current page
            const currentPath = window.location.pathname;
            tubeNav.querySelectorAll('.tube-nav-link:not(.tube-nav-cta)').forEach(link => {
                link.classList.remove('active');
                const href = link.getAttribute('href');
                if (href === '/blog/' && currentPath.includes('/blog/')) {
                    link.classList.add('active');
                } else if (href === currentPath) {
                    link.classList.add('active');
                }
            });
        }"""


def remove_old_floating_cta_css(content):
    """Remove the FLOATING SIDE CTA CSS section."""
    pattern = (
        r'/\*\s*={10,}\s*\n\s*FLOATING SIDE CTA\s*\n\s*={10,}\s*\*/'
        r'.*?'
        r'(?=/\*\s*={10,}\s*\n\s*(?:FLOATING CONTACT|FOOTER))'
    )
    content = re.sub(pattern, '', content, flags=re.DOTALL)
    return content


def remove_old_floating_cta_html(content):
    """Remove floating side CTA HTML."""
    pattern = r'\s*<!-- Floating Side CTA -->.*?</div>\s*</a>\s*</div>\s*</div>'
    content = re.sub(pattern, '', content, flags=re.DOTALL)
    return content


def remove_old_floating_cta_js(content):
    """Remove floating side CTA JS."""
    pattern = r'\s*// -- Floating side CTA --.*?if \(floatingCta\) \{.*?\}'
    content = re.sub(pattern, '', content, flags=re.DOTALL, count=1)
    return content


def replace_header_with_tubenav(content):
    """Replace old <header> with tubelight navbar."""
    if 'tube-nav' in content:
        return content

    # Replace the header HTML
    pattern = r'<header[^>]*>.*?</header>'
    content = re.sub(pattern, NAVBAR_HTML, content, flags=re.DOTALL, count=1)
    return content


def replace_header_css(content):
    """Replace HEADER CSS section with tubelight navbar CSS."""
    if 'TUBELIGHT NAVBAR' in content:
        return content

    pattern = (
        r'/\*\s*={10,}\s*\n\s*HEADER\s*\n\s*={10,}\s*\*/'
        r'.*?'
        r'(?=/\*\s*={10,}\s*\n\s*BLOG HERO)'
    )
    content = re.sub(pattern, NAVBAR_CSS + '\n\n        ', content, flags=re.DOTALL)
    return content


def add_chat_css(content):
    """Add chat widget CSS before the FLOATING CONTACT FAB section."""
    if 'EXPANDABLE CHAT WIDGET' in content:
        return content

    marker = '/* ============================================\n           FLOATING CONTACT FAB'
    idx = content.find(marker)
    if idx != -1:
        content = content[:idx] + CHAT_CSS + '\n\n        ' + content[idx:]
    return content


def add_chat_html(content):
    """Add chat widget HTML before floating contact FAB."""
    if 'chatWidget' in content and '<div class="chat-widget"' in content:
        return content

    marker = '    <!-- Floating Contact FAB -->'
    idx = content.find(marker)
    if idx != -1:
        content = content[:idx] + CHAT_HTML + '\n' + content[idx:]
    return content


def add_chat_js(content):
    """Add chat JS after contact FAB JS."""
    if 'Expandable Chat Widget' in content:
        return content

    marker = """        // -- Contact FAB toggle --
        const contactFab = document.getElementById('contactFab');
        if (contactFab) {
            const fabToggle = contactFab.querySelector('.contact-fab-toggle');
            fabToggle.addEventListener('click', () => {
                contactFab.classList.toggle('open');
            });
            document.addEventListener('click', (e) => {
                if (!contactFab.contains(e.target)) {
                    contactFab.classList.remove('open');
                }
            });
        }"""

    idx = content.find(marker)
    if idx != -1:
        end = idx + len(marker)
        content = content[:end] + CHAT_JS + content[end:]
    return content


def add_navbar_js(content):
    """Add tubelight navbar JS."""
    if 'Tubelight Navbar' in content:
        return content

    # Insert after the reveal observer setup
    marker = "revealElements.forEach(el => revealObserver.observe(el));"
    idx = content.find(marker)
    if idx != -1:
        end = idx + len(marker)
        content = content[:end] + NAVBAR_JS + content[end:]
    return content


def update_responsive(content):
    """Update responsive CSS for header changes."""
    # Remove old header responsive rules
    old_rules = [
        'header { height: 100px; }',
        'header { height: 80px; }',
        '.logo img { width: 180px; }',
        '.logo img { width: 140px; }',
        'nav { display: none; }',
        '.mobile-toggle { display: flex; }',
    ]
    for rule in old_rules:
        content = content.replace('            ' + rule + '\n', '')

    # Remove old mobile nav toggle JS
    pattern = (
        r'\s*// -- Mobile nav toggle --.*?'
        r"mainNav\.querySelectorAll\('a'\)\.forEach\(a => a\.style\.color = ''\);\s*\}\s*\}\);"
    )
    content = re.sub(pattern, '', content, flags=re.DOTALL)

    return content


def main():
    blog_dir = os.path.abspath(BLOG_DIR)
    files = sorted(glob.glob(os.path.join(blog_dir, '*.html')))

    updated = 0
    for f in files:
        basename = os.path.basename(f)
        if basename == 'index.html':
            continue

        with open(f, 'r') as fh:
            content = fh.read()

        original = content

        # Remove old floating side CTA (replaced by chat widget)
        content = remove_old_floating_cta_css(content)
        content = remove_old_floating_cta_html(content)
        content = remove_old_floating_cta_js(content)

        # Add new components
        content = replace_header_css(content)
        content = add_chat_css(content)
        content = add_chat_html(content)
        content = replace_header_with_tubenav(content)
        content = update_responsive(content)
        content = add_navbar_js(content)
        content = add_chat_js(content)

        if content != original:
            with open(f, 'w') as fh:
                fh.write(content)
            print(f'  OK: {basename}')
            updated += 1
        else:
            print(f'  SKIP: {basename}')

    print(f'\nUpdated {updated} files')


if __name__ == '__main__':
    main()
