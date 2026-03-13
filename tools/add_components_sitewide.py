#!/usr/bin/env python3
"""
Add tubelight navbar, chat widget, contact FAB, and back-to-top button
to all non-blog pages: index.html, blog/index.html, cities.html, tools/quote-calculator.html
"""

import os
import re

BASE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')

# ── Shared CSS for all components ──
SHARED_CSS = """
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
            font-family: 'Manrope', system-ui, sans-serif;
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
            color: #001D4A !important;
        }

        .tube-nav-link:hover {
            color: #ECA400 !important;
        }

        .tube-nav-link.active {
            color: #ECA400 !important;
            background: rgba(236, 164, 0, 0.08);
        }

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

            .contact-fab { bottom: 5rem !important; }
            .back-to-top { bottom: 5rem !important; }
        }

        /* ============================================
           EXPANDABLE CHAT WIDGET
           ============================================ */
        .chat-widget {
            position: fixed;
            bottom: 1.5rem;
            right: 1.5rem;
            z-index: 1000;
            font-family: 'Manrope', system-ui, sans-serif;
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
            font-family: 'Bebas Neue', Impact, sans-serif;
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
        }

        /* ============================================
           FLOATING CONTACT FAB
           ============================================ */
        .contact-fab {
            position: fixed;
            bottom: 2rem;
            left: 2rem;
            z-index: 998;
        }

        .contact-fab-toggle {
            width: 54px;
            height: 54px;
            border-radius: 50%;
            border: none;
            background: linear-gradient(135deg, #006992, #005577);
            color: #fff;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            box-shadow: 0 4px 20px rgba(0, 105, 146, 0.4);
            position: relative;
            z-index: 2;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }

        .contact-fab-toggle::after {
            content: '';
            position: absolute;
            inset: -4px;
            border-radius: 50%;
            background: rgba(0, 105, 146, 0.25);
            animation: fabPulse 2s ease-in-out infinite;
            z-index: -1;
        }

        @keyframes fabPulse {
            0%, 100% { transform: scale(1); opacity: 0.5; }
            50% { transform: scale(1.25); opacity: 0; }
        }

        .contact-fab-toggle:hover {
            transform: scale(1.08);
            box-shadow: 0 6px 28px rgba(0, 105, 146, 0.5);
        }

        .contact-fab-toggle svg {
            width: 24px;
            height: 24px;
            fill: none;
            stroke: #fff;
            stroke-width: 2;
            stroke-linecap: round;
            stroke-linejoin: round;
            transition: transform 0.3s;
        }

        .contact-fab.open .contact-fab-toggle svg {
            transform: rotate(45deg);
        }

        .contact-fab.open .contact-fab-toggle {
            background: linear-gradient(135deg, #001D4A, #0a2a5c);
        }

        .contact-fab.open .contact-fab-toggle::after {
            animation: none;
            opacity: 0;
        }

        .contact-fab-menu {
            position: absolute;
            bottom: 68px;
            left: 0;
            display: flex;
            flex-direction: column;
            gap: 0.6rem;
            opacity: 0;
            visibility: hidden;
            transform: translateY(12px) scale(0.9);
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }

        .contact-fab.open .contact-fab-menu {
            opacity: 1;
            visibility: visible;
            transform: translateY(0) scale(1);
        }

        .contact-fab-item {
            display: flex;
            align-items: center;
            gap: 0.65rem;
            padding: 0.6rem 1rem 0.6rem 0.6rem;
            background: #fff;
            border-radius: 28px;
            text-decoration: none !important;
            box-shadow: 0 3px 16px rgba(0, 0, 0, 0.12), 0 0 0 1px rgba(0, 0, 0, 0.04);
            white-space: nowrap;
            transform: translateY(8px);
            opacity: 0;
            transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
        }

        .contact-fab.open .contact-fab-item {
            transform: translateY(0);
            opacity: 1;
        }

        .contact-fab.open .contact-fab-item:nth-child(1) { transition-delay: 0.05s; }
        .contact-fab.open .contact-fab-item:nth-child(2) { transition-delay: 0.1s; }
        .contact-fab.open .contact-fab-item:nth-child(3) { transition-delay: 0.15s; }

        .contact-fab-item:hover {
            box-shadow: 0 6px 24px rgba(0, 0, 0, 0.15), 0 0 0 1px rgba(0, 105, 146, 0.15);
            transform: translateX(4px);
        }

        .fab-icon {
            width: 38px;
            height: 38px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            flex-shrink: 0;
        }

        .fab-icon svg {
            width: 18px;
            height: 18px;
            fill: none;
            stroke: #fff;
            stroke-width: 2;
            stroke-linecap: round;
            stroke-linejoin: round;
        }

        .fab-icon-call { background: linear-gradient(135deg, #22c55e, #16a34a); }
        .fab-icon-text { background: linear-gradient(135deg, #006992, #005577); }
        .fab-icon-email { background: linear-gradient(135deg, #ECA400, #d4940a); }
        .fab-icon-email svg { stroke: #001D4A; }

        .fab-label {
            font-size: 0.82rem;
            font-weight: 600;
            color: #001D4A !important;
            line-height: 1.2;
        }

        .fab-label span {
            display: block;
            font-size: 0.7rem;
            font-weight: 400;
            color: #6b7280 !important;
            margin-top: 1px;
        }

        @media (max-width: 768px) {
            .contact-fab {
                bottom: 4.5rem;
                left: 1.25rem;
            }
            .contact-fab-toggle {
                width: 48px;
                height: 48px;
            }
            .contact-fab-toggle svg {
                width: 22px;
                height: 22px;
            }
            .contact-fab-menu {
                bottom: 60px;
            }
        }

        /* ============================================
           BACK TO TOP
           ============================================ */
        .back-to-top {
            position: fixed;
            bottom: 2rem;
            right: 2rem;
            width: 44px;
            height: 44px;
            background: linear-gradient(135deg, #ECA400, #d4940a);
            border: none;
            border-radius: 50%;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            box-shadow: 0 4px 16px rgba(236, 164, 0, 0.35);
            opacity: 0;
            visibility: hidden;
            transform: translateY(10px);
            transition: all 0.35s cubic-bezier(0.4, 0, 0.2, 1);
            z-index: 999;
        }

        .back-to-top.visible {
            opacity: 1;
            visibility: visible;
            transform: translateY(0);
        }

        .back-to-top:hover {
            transform: translateY(-3px);
            box-shadow: 0 6px 24px rgba(236, 164, 0, 0.5);
        }

        .back-to-top svg {
            width: 20px;
            height: 20px;
            stroke: #001D4A;
            fill: none;
            stroke-width: 2.5;
            stroke-linecap: round;
            stroke-linejoin: round;
        }

        @media (max-width: 640px) {
            .back-to-top { bottom: 1.5rem; right: 1.5rem; width: 40px; height: 40px; }
        }
"""

# ── Tubelight Navbar HTML ──
def get_navbar_html(logo_path, active_page):
    """Generate navbar HTML with correct logo path and active page."""
    def active(page):
        return ' active' if page == active_page else ''

    return f'''    <div class="tube-nav" id="tubeNav">
        <div class="tube-nav-inner">
            <a href="/" class="tube-nav-logo" aria-label="Blue Brick Home">
                <img src="{logo_path}" alt="Blue Brick">
            </a>
            <a href="/#services" class="tube-nav-link{active('services')}">
                <span class="nav-label">Services</span>
                <span class="nav-icon"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z"/></svg></span>
            </a>
            <a href="/cities.html" class="tube-nav-link{active('areas')}">
                <span class="nav-label">Areas</span>
                <span class="nav-icon"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/><circle cx="12" cy="10" r="3"/></svg></span>
            </a>
            <a href="/blog/" class="tube-nav-link{active('blog')}">
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
'''

# ── Chat Widget HTML ──
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

# ── Contact FAB HTML ──
CONTACT_FAB_HTML = """
    <!-- Floating Contact FAB -->
    <div class="contact-fab" id="contactFab">
        <div class="contact-fab-menu">
            <a href="tel:+17813305604" class="contact-fab-item">
                <div class="fab-icon fab-icon-call">
                    <svg viewBox="0 0 24 24"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72c.127.96.361 1.903.7 2.81a2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45c.907.339 1.85.573 2.81.7A2 2 0 0 1 22 16.92z"/></svg>
                </div>
                <div class="fab-label">Call Now<span>(781) 330-5604</span></div>
            </a>
            <a href="sms:+17813305604" class="contact-fab-item">
                <div class="fab-icon fab-icon-text">
                    <svg viewBox="0 0 24 24"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>
                </div>
                <div class="fab-label">Text Now<span>(781) 330-5604</span></div>
            </a>
            <a href="mailto:bluebrickmass@gmail.com" class="contact-fab-item">
                <div class="fab-icon fab-icon-email">
                    <svg viewBox="0 0 24 24"><path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/><polyline points="22,6 12,13 2,6"/></svg>
                </div>
                <div class="fab-label">Email Us<span>bluebrickmass@gmail.com</span></div>
            </a>
        </div>
        <button class="contact-fab-toggle" aria-label="Contact us">
            <svg viewBox="0 0 24 24"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>
        </button>
    </div>
"""

# ── Back to Top HTML ──
BACK_TO_TOP_HTML = """
    <!-- Back to Top Button -->
    <button class="back-to-top" id="backToTop" aria-label="Back to top">
        <svg viewBox="0 0 24 24"><polyline points="18 15 12 9 6 15"/></svg>
    </button>
"""

# ── Shared JS for all widgets ──
SHARED_JS = """
    <script>
        // -- Tubelight Navbar --
        var tubeNav = document.getElementById('tubeNav');
        if (tubeNav) {
            window.addEventListener('scroll', function() {
                if (window.scrollY > 100) {
                    tubeNav.classList.add('scrolled');
                } else {
                    tubeNav.classList.remove('scrolled');
                }
            });

            var currentPath = window.location.pathname;
            tubeNav.querySelectorAll('.tube-nav-link:not(.tube-nav-cta)').forEach(function(link) {
                link.classList.remove('active');
                var href = link.getAttribute('href');
                if (href === '/blog/' && currentPath.includes('/blog/')) {
                    link.classList.add('active');
                } else if (href === '/cities.html' && currentPath.includes('cities')) {
                    link.classList.add('active');
                } else if (href === '/' && (currentPath === '/' || currentPath === '/index.html')) {
                    // Home page - no active state needed for services link
                } else if (href === currentPath) {
                    link.classList.add('active');
                }
            });
        }

        // -- Back to Top button --
        var backToTop = document.getElementById('backToTop');
        if (backToTop) {
            window.addEventListener('scroll', function() {
                if (window.scrollY > 600) {
                    backToTop.classList.add('visible');
                } else {
                    backToTop.classList.remove('visible');
                }
            });
            backToTop.addEventListener('click', function() {
                window.scrollTo({ top: 0, behavior: 'smooth' });
            });
        }

        // -- Contact FAB toggle --
        var contactFab = document.getElementById('contactFab');
        if (contactFab) {
            var fabToggle = contactFab.querySelector('.contact-fab-toggle');
            fabToggle.addEventListener('click', function() {
                contactFab.classList.toggle('open');
            });
            document.addEventListener('click', function(e) {
                if (!contactFab.contains(e.target)) {
                    contactFab.classList.remove('open');
                }
            });
        }

        // -- Expandable Chat Widget --
        var chatWidget2 = document.getElementById('chatWidget');
        var chatToggle2 = document.getElementById('chatToggle');
        var chatInput2 = document.getElementById('chatInput');
        var chatSendBtn2 = document.getElementById('chatSendBtn');
        var chatBody2 = document.getElementById('chatBody');

        if (chatToggle2 && chatWidget2) {
            chatToggle2.addEventListener('click', function(e) {
                e.stopPropagation();
                chatWidget2.classList.toggle('open');
                if (chatWidget2.classList.contains('open') && chatInput2) {
                    setTimeout(function() { chatInput2.focus(); }, 300);
                }
            });

            var chatResponses = {
                quote: "Great! For a quick estimate, try our <a href='/tools/quote-calculator.html' target='_blank' style='color:#ECA400;font-weight:600'>Quote Calculator</a> or text us at <a href='sms:+17813305604' style='color:#ECA400;font-weight:600'>(781) 330-5604</a> with your address and sqft!",
                services: "We offer: Deep Cleaning, Post-Construction Cleanup, Move-In/Move-Out, Luxury Residential, Commercial Cleaning, and Spring Cleaning. Which interests you?",
                areas: "We serve 15 cities: Boston, Cambridge, Newton, Waltham, Brookline, Somerville, Brighton, Watertown, Allston, East Boston, South Boston, Lexington, Needham, Wellesley, and Weston!",
                price: "Pricing depends on square footage and service type. Use our <a href='/tools/quote-calculator.html' target='_blank' style='color:#ECA400;font-weight:600'>Quote Calculator</a> for an instant estimate!",
                book: "To book, text us at <a href='sms:+17813305604' style='color:#ECA400;font-weight:600'>(781) 330-5604</a> or email <a href='mailto:bluebrickmass@gmail.com' style='color:#ECA400;font-weight:600'>bluebrickmass@gmail.com</a>. We respond within 2 hours!",
                fallback: "Thanks for your message! For the fastest response, text us at <a href='sms:+17813305604' style='color:#ECA400;font-weight:600'>(781) 330-5604</a> or email <a href='mailto:bluebrickmass@gmail.com' style='color:#ECA400;font-weight:600'>bluebrickmass@gmail.com</a>."
            };

            function chatAddMsg(text, isSent) {
                var msg = document.createElement('div');
                msg.className = 'chat-msg' + (isSent ? ' sent' : '');
                msg.innerHTML = '<div class="chat-msg-avatar">' + (isSent ? 'You' : 'BB') + '</div><div class="chat-msg-bubble">' + text + '</div>';
                chatBody2.appendChild(msg);
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

            function chatGetResponse(text) {
                var t = text.toLowerCase();
                if (t.indexOf('quote') > -1 || t.indexOf('estimate') > -1 || t.indexOf('cost') > -1) return chatResponses.quote;
                if (t.indexOf('service') > -1 || t.indexOf('offer') > -1 || t.indexOf('clean') > -1) return chatResponses.services;
                if (t.indexOf('area') > -1 || t.indexOf('city') > -1 || t.indexOf('where') > -1 || t.indexOf('cover') > -1) return chatResponses.areas;
                if (t.indexOf('price') > -1 || t.indexOf('how much') > -1 || t.indexOf('rate') > -1) return chatResponses.price;
                if (t.indexOf('book') > -1 || t.indexOf('schedule') > -1 || t.indexOf('appointment') > -1) return chatResponses.book;
                return chatResponses.fallback;
            }

            function chatHandleSend() {
                var text = chatInput2.value.trim();
                if (!text) return;
                chatAddMsg(text, true);
                chatInput2.value = '';
                chatAddLoading();
                setTimeout(function() {
                    var loader = document.getElementById('chatLoader');
                    if (loader) loader.remove();
                    chatAddMsg(chatGetResponse(text), false);
                }, 800 + Math.random() * 600);
            }

            chatSendBtn2.addEventListener('click', chatHandleSend);
            chatInput2.addEventListener('keydown', function(e) {
                if (e.key === 'Enter') { e.preventDefault(); chatHandleSend(); }
            });

            document.querySelectorAll('.chat-quick-btn').forEach(function(btn) {
                btn.addEventListener('click', function() {
                    chatInput2.value = btn.getAttribute('data-msg');
                    chatHandleSend();
                });
            });

            document.addEventListener('click', function(e) {
                if (!chatWidget2.contains(e.target) && chatWidget2.classList.contains('open')) {
                    chatWidget2.classList.remove('open');
                }
            });
        }
    </script>
"""


def process_file(filepath, logo_path, active_page):
    """Add all components to a single file."""
    with open(filepath, 'r') as f:
        content = f.read()

    original = content
    basename = os.path.basename(filepath)

    # Skip if already has tube-nav
    if 'tube-nav' in content and 'id="tubeNav"' in content:
        print(f'  SKIP (already has tube-nav): {filepath}')
        return False

    # 1. Add CSS before </style>
    style_close_idx = content.rfind('</style>')
    if style_close_idx != -1:
        content = content[:style_close_idx] + SHARED_CSS + '\n    </style>' + content[style_close_idx + len('</style>'):]
    else:
        print(f'  ERROR: No </style> found in {filepath}')
        return False

    # 2. Replace old header with tubelight navbar
    navbar_html = get_navbar_html(logo_path, active_page)

    # Try different header patterns
    # Pattern A: <header id="header" ...>...</header> (homepage, cities)
    header_match = re.search(
        r'\s*(?:<!-- ={3,}.*?HEADER.*?={3,} -->\s*)?<header[^>]*>.*?</header>',
        content,
        re.DOTALL
    )
    if header_match:
        content = content[:header_match.start()] + '\n' + navbar_html + content[header_match.end():]
        print(f'    Replaced header with tube-nav')
    else:
        # Pattern B: quote-calculator has <div class="header"> not <header>
        header_div_match = re.search(r'<div class="header">.*?</div>\s*\n', content, re.DOTALL)
        if header_div_match:
            # Insert tube-nav before the header div (keep header div for calculator)
            insert_idx = header_div_match.start()
            content = content[:insert_idx] + navbar_html + '\n' + content[insert_idx:]
            print(f'    Added tube-nav before calculator header')
        else:
            # Just insert after <body>
            body_match = re.search(r'<body[^>]*>', content)
            if body_match:
                insert_idx = body_match.end()
                content = content[:insert_idx] + '\n' + navbar_html + content[insert_idx:]
                print(f'    Added tube-nav after <body>')

    # 3. Remove old mobile toggle JS (won't work with new navbar)
    content = re.sub(
        r"\s*//\s*──?\s*Mobile nav.*?(?=\s*</script>|\s*//\s*──)",
        '\n',
        content,
        flags=re.DOTALL
    )

    # 4. Add floating widgets HTML before </body>
    body_close_idx = content.rfind('</body>')
    if body_close_idx != -1:
        widgets = CHAT_HTML + CONTACT_FAB_HTML + BACK_TO_TOP_HTML + SHARED_JS + '\n'
        content = content[:body_close_idx] + widgets + content[body_close_idx:]
        print(f'    Added chat widget, contact FAB, back-to-top, and JS')

    if content != original:
        with open(filepath, 'w') as f:
            f.write(content)
        print(f'  OK: {filepath}')
        return True
    else:
        print(f'  NO CHANGES: {filepath}')
        return False


def main():
    files = [
        {
            'path': os.path.join(BASE_DIR, 'index.html'),
            'logo': 'assets/images/IMG_9670.png',
            'active': 'home',
        },
        {
            'path': os.path.join(BASE_DIR, 'blog', 'index.html'),
            'logo': '../assets/images/IMG_9670.png',
            'active': 'blog',
        },
        {
            'path': os.path.join(BASE_DIR, 'cities.html'),
            'logo': 'assets/images/IMG_9670.png',
            'active': 'areas',
        },
        {
            'path': os.path.join(BASE_DIR, 'tools', 'quote-calculator.html'),
            'logo': '../assets/images/IMG_9670.png',
            'active': '',  # No active link for calculator
        },
    ]

    updated = 0
    for f in files:
        filepath = os.path.abspath(f['path'])
        if not os.path.exists(filepath):
            print(f'  NOT FOUND: {filepath}')
            continue

        print(f'\nProcessing: {filepath}')
        if process_file(filepath, f['logo'], f['active']):
            updated += 1

    print(f'\n\nUpdated {updated} files')


if __name__ == '__main__':
    main()
