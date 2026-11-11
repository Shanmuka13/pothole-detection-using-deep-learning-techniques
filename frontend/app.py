import os
from urllib.parse import quote

import pandas as pd
import requests
import streamlit as st
import streamlit.components.v1 as components
from streamlit_cookies_controller import CookieController
from streamlit_geolocation import streamlit_geolocation
from PIL import Image

BACKEND_BASE_URL = os.getenv("BACKEND_BASE_URL", "http://127.0.0.1:8001").rstrip("/")
MEDIA_TYPES = ["jpg", "jpeg", "png", "webp", "mp4"]
VIDEO_TYPES = {"mp4"}
DEFAULT_LOCATION_ADDRESS = "Vignan University, Vadlamudi, Guntur District, Andhra Pradesh 522213, India"
DEFAULT_LOCATION_PINCODE = "522213"
DEFAULT_LOCATION_LATITUDE = 16.2366
DEFAULT_LOCATION_LONGITUDE = 80.5519

# 1. Page Configuration
st.set_page_config(page_title="Pothole Detection", page_icon="🛰️", layout="wide", initial_sidebar_state="expanded")
cookie_controller = CookieController()
ROLE_COOKIE = "pothole_detection_role"
TOKEN_COOKIE = "pothole_detection_token"
ACCOUNT_COOKIE = "pothole_detection_account"
SESSION_COOKIE_MAX_AGE = 7 * 24 * 60 * 60

# 2. App styling
st.markdown("""
<style>
    :root {
        --up-ink: #151515;
        --up-muted: #5b6068;
        --up-teal: #151515;
        --up-coral: #c45b3c;
        --up-sky: #fff4ec;
        --up-line: #dedbd7;
    }
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(15px); }
        to { opacity: 1; transform: translateY(0); }
    }
    @keyframes heroBreath {
        0%, 100% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
    }
    @keyframes driftIn {
        from { opacity: 0; transform: translateY(24px) scale(.98); }
        to { opacity: 1; transform: translateY(0) scale(1); }
    }
    @keyframes techFloat {
        0%, 100% { transform: translate3d(0, 0, 0) rotate(-4deg); }
        50% { transform: translate3d(18px, -12px, 0) rotate(4deg); }
    }
    @keyframes potholePulse {
        0%, 100% { transform: scale(.92); opacity: .46; box-shadow: 0 0 0 0 rgba(223,255,120,.24); }
        50% { transform: scale(1.05); opacity: .9; box-shadow: 0 0 0 16px rgba(223,255,120,0); }
    }
    @keyframes scanLine {
        0% { transform: translateX(-120%); opacity: 0; }
        18%, 72% { opacity: .7; }
        100% { transform: translateX(420%); opacity: 0; }
    }
    .animated-element {
        animation: fadeIn 0.5s ease-out forwards;
    }
    .tech-watermark {
        position: fixed;
        right: 2.5rem;
        bottom: 1.4rem;
        z-index: 0;
        pointer-events: none;
        color: rgba(31, 65, 45, .13);
        font-size: .62rem;
        font-weight: 850;
        letter-spacing: .28em;
        text-transform: uppercase;
        animation: techFloat 9s ease-in-out infinite;
    }
    .tech-watermark span { margin-left: 1.1rem; }
    .pothole-orbit {
        position: fixed;
        left: 17rem;
        bottom: 1.35rem;
        z-index: 0;
        width: 1.3rem;
        height: .7rem;
        border: 1px solid rgba(196,91,60,.22);
        border-radius: 50%;
        pointer-events: none;
        animation: potholePulse 4.5s ease-in-out infinite;
    }
    .pothole-orbit:before, .pothole-orbit:after {
        position: absolute;
        content: "";
        border: 1px solid rgba(196,91,60,.16);
        border-radius: 50%;
    }
    .pothole-orbit:before { inset: -.45rem -.8rem; }
    .pothole-orbit:after { inset: -.9rem -1.5rem; }
    .landing-shell {
        padding: 1.2rem 0 2rem;
        color: var(--up-ink);
        background-image: linear-gradient(rgba(21,21,21,.055) 1px, transparent 1px), linear-gradient(90deg, rgba(21,21,21,.055) 1px, transparent 1px);
        background-size: 32px 32px;
    }
    .landing-hero {
        position: relative;
        overflow: hidden;
        min-height: 430px;
        padding: clamp(2rem, 6vw, 5.5rem);
        border-radius: 22px;
        background: linear-gradient(120deg, #111111 0%, #292929 55%, #a94f36 100%);
        background-size: 180% 180%;
        color: white;
        box-shadow: 0 18px 45px rgba(21, 21, 21, 0.18);
        animation: heroBreath 14s ease-in-out infinite;
    }
    .landing-hero:after {
        content: "";
        position: absolute;
        width: 390px;
        height: 390px;
        right: -90px;
        top: -120px;
        border: 1px solid rgba(255,255,255,.24);
        border-radius: 50%;
        box-shadow: 0 0 0 38px rgba(255,255,255,.07), 0 0 0 76px rgba(255,255,255,.045);
    }
    .landing-kicker {
        position: relative;
        z-index: 1;
        margin-bottom: 1rem;
        color: #ffe0cc;
        font-size: .78rem;
        font-weight: 800;
        letter-spacing: .12em;
        text-transform: uppercase;
    }
    .landing-hero h1 {
        position: relative;
        z-index: 1;
        max-width: 730px;
        margin: 0;
        color: white;
        font-size: clamp(2.6rem, 6vw, 5.4rem);
        line-height: .98;
        letter-spacing: -.04em;
    }
    .landing-hero p {
        position: relative;
        z-index: 1;
        max-width: 650px;
        margin: 1.5rem 0 0;
        color: #f8eee8;
        font-size: 1.08rem;
        line-height: 1.65;
        transition: color .35s ease, transform .35s ease;
    }
    .landing-hero p:hover {
        color: #ffffff;
        transform: translateX(8px);
    }
    .landing-section {
        padding: 4rem 0 1rem;
    }
    .landing-section h2 {
        margin-bottom: .55rem;
        color: var(--up-ink);
        font-size: clamp(1.8rem, 3vw, 2.65rem);
        letter-spacing: -.03em;
        transition: color .35s ease, letter-spacing .35s ease, transform .35s ease;
    }
    .landing-section h2:hover {
        color: var(--up-coral);
        letter-spacing: .01em;
        transform: translateX(6px);
    }
    .landing-section-intro {
        max-width: 690px;
        margin-bottom: 1.7rem;
        color: var(--up-muted);
        font-size: 1.02rem;
        line-height: 1.65;
        transition: color .35s ease, transform .35s ease;
    }
    .landing-section-intro:hover {
        color: var(--up-ink);
        transform: translateX(5px);
    }
    .landing-card {
        height: 100%;
        padding: 1.5rem;
        border: 1px solid var(--up-line);
        border-radius: 12px;
        background: rgba(255,255,255,.74);
        transition: transform .3s cubic-bezier(.2,.8,.2,1), box-shadow .3s ease, border-color .3s ease, background .3s ease;
    }
    .landing-card:hover {
        transform: translateY(-7px) scale(1.015);
        border-color: var(--up-ink);
        box-shadow: 0 14px 30px rgba(21,21,21,.14);
    }
    .landing-card h3 {
        margin: .7rem 0 .4rem;
        color: var(--up-ink);
        font-size: 1.15rem;
    }
    .landing-card p {
        margin: 0;
        color: var(--up-muted);
        line-height: 1.55;
        transition: color .35s ease, transform .35s ease;
    }
    .landing-card:hover p {
        color: var(--up-ink);
        transform: translateX(3px);
    }
    .landing-icon {
        display: inline-grid;
        width: 2.45rem;
        height: 2.45rem;
        place-items: center;
        border-radius: 9px;
        background: var(--up-sky);
        color: var(--up-teal);
        font-size: 1.25rem;
    }
    .landing-step {
        color: var(--up-coral);
        font-size: .78rem;
        font-weight: 800;
        letter-spacing: .1em;
        transition: letter-spacing .35s ease, color .35s ease;
    }
    .landing-card:hover .landing-step {
        color: var(--up-ink);
        letter-spacing: .22em;
    }
    .landing-finale {
        margin-top: 4rem;
        padding: 2.5rem 2rem 3rem;
        border-top: 1px solid var(--up-line);
        text-align: center;
    }
    .landing-finale p {
        color: var(--up-muted);
    }
    .landing-availability {
        display: grid;
        grid-template-columns: 1.25fr .75fr;
        gap: 1.5rem;
        align-items: stretch;
        margin-top: 1.5rem;
    }
    .landing-availability-copy {
        padding: 1.8rem;
        border-left: 4px solid var(--up-coral);
        background: rgba(255,255,255,.72);
    }
    .landing-availability-copy h3 { margin-top: 0; color: var(--up-ink); }
    .landing-availability-copy p { color: var(--up-muted); line-height: 1.6; }
    .landing-availability-copy p { transition: color .35s ease, transform .35s ease; }
    .landing-availability-copy p:hover { color: var(--up-ink); transform: translateX(5px); }
    .landing-metrics {
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        gap: .75rem;
    }
    .landing-metric {
        padding: 1.15rem;
        border: 1px solid var(--up-line);
        background: rgba(231,246,247,.75);
        transition: transform .25s ease, background .25s ease, border-color .25s ease;
    }
    .landing-metric:hover {
        transform: translateY(-4px) rotate(-1deg);
        border-color: var(--up-ink);
        background: var(--up-sky);
    }
    .landing-metric strong { display: block; color: var(--up-ink); font-size: 1.55rem; }
    .landing-metric span { color: var(--up-muted); font-size: .85rem; }
    @media (prefers-color-scheme: dark) {
        :root {
            --up-ink: #effcf9;
            --up-muted: #a7c2c0;
            --up-teal: #6fe0d0;
            --up-coral: #ffae73;
            --up-sky: #163536;
            --up-line: #315452;
        }
        .landing-shell {
            background-color: #081c20;
            background-image: radial-gradient(circle at 85% 8%, rgba(76,191,177,.17), transparent 24rem), linear-gradient(90deg, rgba(255,255,255,.035) 1px, transparent 1px);
            background-size: auto, 56px 56px;
        }
        .landing-hero {
            min-height: 520px;
            border-radius: 4px;
            background: #102e32;
            border: 1px solid #3b6864;
            box-shadow: 0 24px 80px rgba(0,0,0,.32);
        }
        .landing-hero:after { right: 8%; top: 12%; width: 300px; height: 300px; border-color: rgba(111,224,208,.35); box-shadow: 0 0 0 52px rgba(111,224,208,.06), 0 0 0 104px rgba(111,224,208,.035); }
        .landing-hero h1 { max-width: 590px; font-size: clamp(2.8rem, 6vw, 5.8rem); }
        .landing-hero p { color: #c9efea; }
        .landing-card, .landing-availability-copy { border-radius: 4px; background: rgba(16,46,50,.84); }
        .landing-availability-copy { background: rgba(16,46,50,.84); }
        .landing-metric { border-radius: 4px; background: rgba(22,53,54,.84); }
        .landing-finale { border-top-color: var(--up-line); }
    }
    @media (prefers-reduced-motion: reduce) {
        *, *::before, *::after {
            animation-duration: .01ms !important;
            animation-iteration-count: 1 !important;
            scroll-behavior: auto !important;
            transition-duration: .01ms !important;
        }
    }
    @media (max-width: 700px) {
        .landing-hero { min-height: 390px; padding: 2rem 1.4rem; }
        .landing-hero:after { right: -190px; }
        .landing-section { padding-top: 2.8rem; }
        .landing-availability { grid-template-columns: 1fr; }
        .landing-metrics { grid-template-columns: repeat(2, 1fr); }
    }
    :root {
        --up-ink: #1c1c1b;
        --up-muted: #66635f;
        --up-teal: #1c1c1b;
        --up-coral: #bd6348;
        --up-sky: #f5e9e1;
        --up-line: #e4dfda;
        --up-paper: #faf9f7;
    }
    html, body, [data-testid="stAppViewContainer"] {
        background: var(--up-paper);
        color: var(--up-ink);
    }
    [data-testid="stMainBlockContainer"] {
        width: 100%;
        max-width: 1600px;
        padding: 1.5rem clamp(1rem, 3.4vw, 3.25rem) 4rem;
    }
    [data-testid="stHeader"] {
        background: transparent;
    }
    [data-testid="stSidebar"] {
        border-right: 1px solid var(--up-line);
        background: #f4f1ed;
    }
    .landing-shell {
        max-width: 1500px;
        margin: 0 auto;
        padding: 0 0 1rem;
        background-image:
            linear-gradient(rgba(28,28,27,.035) 1px, transparent 1px),
            linear-gradient(90deg, rgba(28,28,27,.035) 1px, transparent 1px);
        background-size: 34px 34px;
    }
    .landing-hero {
        box-sizing: border-box;
        display: flex;
        min-height: 520px;
        flex-direction: column;
        justify-content: center;
        padding: clamp(2.25rem, 5vw, 4.5rem) clamp(2.25rem, 7vw, 6rem);
        border: 1px solid rgba(255,255,255,.1);
        border-radius: 24px;
        background:
            radial-gradient(ellipse at 92% 8%, rgba(198,104,75,.38), transparent 34%),
            linear-gradient(112deg, #20201f 0%, #302725 57%, #8e4937 100%);
        background-size: auto;
        box-shadow: 0 24px 70px rgba(37,28,24,.16);
        animation: none;
    }
    .landing-hero:after {
        right: -5%;
        top: -26%;
        width: clamp(250px, 36vw, 470px);
        height: clamp(250px, 36vw, 470px);
        border-color: rgba(255,255,255,.16);
        box-shadow: 0 0 0 34px rgba(255,255,255,.055), 0 0 0 70px rgba(255,255,255,.035);
        pointer-events: none;
    }
    .landing-kicker {
        margin-bottom: 1.5rem;
        color: #f2c9b8;
        font-size: .76rem;
        letter-spacing: .14em;
    }
    .landing-hero h1 {
        max-width: 660px;
        font-size: clamp(3rem, 6.2vw, 5.5rem);
        line-height: .99;
        letter-spacing: -.055em;
        text-wrap: balance;
    }
    .landing-hero p {
        max-width: 680px;
        margin-top: 1.55rem;
        color: #eee5e0;
        font-size: clamp(1rem, 1.35vw, 1.15rem);
        line-height: 1.75;
    }
    .landing-hero p:hover {
        transform: none;
    }
    .landing-section {
        padding: clamp(3.25rem, 6vw, 5.25rem) 0 1rem;
    }
    .landing-section h2 {
        max-width: 820px;
        font-size: clamp(1.8rem, 3.4vw, 2.75rem);
        line-height: 1.12;
        letter-spacing: -.045em;
        text-wrap: balance;
    }
    .landing-section h2:hover {
        color: var(--up-ink);
        letter-spacing: -.045em;
        transform: none;
    }
    .landing-section-intro {
        max-width: 720px;
        margin: .8rem 0 1.75rem;
        line-height: 1.75;
    }
    .landing-section-intro:hover,
    .landing-availability-copy p:hover {
        transform: none;
    }
    .landing-card {
        min-height: 100%;
        padding: clamp(1.35rem, 2.5vw, 2rem);
        border: 1px solid var(--up-line);
        border-radius: 16px;
        background: rgba(255,255,255,.82);
        box-shadow: 0 8px 26px rgba(28,28,27,.035);
    }
    .landing-card:hover {
        transform: translateY(-4px);
        border-color: #cbbeb5;
        box-shadow: 0 16px 34px rgba(28,28,27,.09);
    }
    .landing-card h3 {
        margin-top: 1rem;
        font-size: 1.2rem;
        letter-spacing: -.02em;
    }
    .landing-card p {
        line-height: 1.7;
    }
    .landing-card:hover p {
        transform: none;
    }
    .landing-icon {
        width: 2.8rem;
        height: 2.8rem;
        border-radius: 12px;
        background: var(--up-sky);
    }
    .landing-step {
        color: var(--up-coral);
        letter-spacing: .14em;
    }
    .landing-card:hover .landing-step {
        color: var(--up-coral);
        letter-spacing: .14em;
    }
    .landing-availability {
        grid-template-columns: minmax(0, 1.2fr) minmax(260px, .8fr);
        gap: 1.25rem;
    }
    .landing-availability-copy {
        padding: clamp(1.4rem, 3vw, 2.25rem);
        border: 1px solid var(--up-line);
        border-left: 4px solid var(--up-coral);
        border-radius: 16px;
        background: rgba(255,255,255,.82);
    }
    .landing-availability-copy p {
        line-height: 1.75;
    }
    .landing-metrics {
        gap: .85rem;
    }
    .landing-metric {
        display: flex;
        min-height: 110px;
        flex-direction: column;
        justify-content: center;
        gap: .35rem;
        padding: 1.15rem;
        border: 1px solid var(--up-line);
        border-radius: 14px;
        background: #f2efeb;
    }
    .landing-metric:hover {
        transform: translateY(-3px);
        border-color: #cbbeb5;
        background: #f5e9e1;
    }
    .landing-metric strong {
        font-size: 1.7rem;
        letter-spacing: -.04em;
    }
    .landing-metric span {
        line-height: 1.4;
    }
    .landing-finale {
        margin-top: 3.5rem;
        padding: 3rem 1rem 1.5rem;
        border-top-color: var(--up-line);
    }
    .landing-finale h2 {
        letter-spacing: -.04em;
    }
    [data-testid="stButton"] > button,
    [data-testid="stFormSubmitButton"] > button {
        min-height: 2.9rem;
        border-radius: 10px;
        font-weight: 650;
        transition: transform .18s ease, box-shadow .18s ease, border-color .18s ease;
    }
    [data-testid="stButton"] > button:hover,
    [data-testid="stFormSubmitButton"] > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 8px 20px rgba(28,28,27,.1);
    }
    [data-testid="stTextInput"] input,
    [data-testid="stTextArea"] textarea,
    [data-testid="stSelectbox"] [role="combobox"],
    [data-testid="stFileUploader"] section {
        border-radius: 10px;
    }
    [data-testid="stMetric"] {
        padding: 1rem 1.1rem;
        border: 1px solid var(--up-line);
        border-radius: 14px;
        background: rgba(255,255,255,.78);
    }
    [data-testid="stVerticalBlockBorderWrapper"] {
        border-color: var(--up-line);
        border-radius: 16px;
    }
    [data-testid="stDataFrame"], [data-testid="stTable"] {
        border: 1px solid var(--up-line);
        border-radius: 12px;
        overflow: hidden;
    }
    @media (prefers-color-scheme: dark) {
        :root {
            --up-ink: #1c1c1b;
            --up-muted: #66635f;
            --up-teal: #1c1c1b;
            --up-coral: #bd6348;
            --up-sky: #f5e9e1;
            --up-line: #e4dfda;
            --up-paper: #faf9f7;
        }
        html, body, [data-testid="stAppViewContainer"] { background: var(--up-paper); color: var(--up-ink); }
        [data-testid="stSidebar"] { background: #f4f1ed; }
        .landing-shell { background-color: transparent; }
        .landing-hero {
            border-color: rgba(255,255,255,.1);
            background:
                radial-gradient(ellipse at 92% 8%, rgba(198,104,75,.38), transparent 34%),
                linear-gradient(112deg, #20201f 0%, #302725 57%, #8e4937 100%);
        }
        .landing-hero h1 { max-width: 660px; font-size: clamp(3rem, 6.2vw, 5.5rem); }
        .landing-hero p { color: #eee5e0; }
        .landing-card, .landing-availability-copy { border-radius: 16px; background: rgba(255,255,255,.82); }
        .landing-metric { border-radius: 14px; background: #f2efeb; }
    }
    @media (max-width: 760px) {
        [data-testid="stMainBlockContainer"] { padding: 1rem 1rem 3rem; }
        .landing-hero { min-height: 430px; padding: 2.25rem 1.5rem; border-radius: 18px; }
        .landing-hero:after { right: -210px; top: -70px; }
        .landing-hero h1 { max-width: 100%; font-size: clamp(2.8rem, 11vw, 4.25rem); }
        .landing-hero p { max-width: 100%; font-size: 1rem; }
        .landing-section { padding-top: 3rem; }
        .landing-availability { grid-template-columns: 1fr; }
    }
    @media (max-width: 480px) {
        .landing-hero { min-height: 400px; padding: 2rem 1.25rem; }
        .landing-kicker { font-size: .67rem; letter-spacing: .1em; }
        .landing-metrics { gap: .6rem; }
        .landing-metric { min-height: 96px; padding: .9rem; }
    }
    @media (prefers-reduced-motion: reduce) {
        *, *::before, *::after { animation: none !important; transition: none !important; scroll-behavior: auto !important; }
    }
    .landing-shell {
        max-width: 1500px;
        margin: 0 auto;
        padding: 1rem 0 2.5rem;
        background: none;
    }
    .landing-nav {
        display: flex;
        min-height: 56px;
        align-items: center;
        gap: .8rem;
        margin-bottom: 1.15rem;
        color: #17211e;
    }
    .landing-brand-mark {
        display: grid;
        width: 38px;
        height: 38px;
        place-items: center;
        border-radius: 12px;
        background: #dfff78;
        color: #17211e;
        font-size: .78rem;
        font-weight: 900;
        letter-spacing: -.06em;
    }
    .landing-brand-name {
        font-size: .98rem;
        font-weight: 800;
        letter-spacing: -.035em;
    }
    .landing-nav-label {
        margin-left: auto;
        padding: .5rem .85rem;
        border: 1px solid #e6e8df;
        border-radius: 999px;
        color: #626c63;
        font-size: .74rem;
        font-weight: 650;
    }
    .landing-hero {
        display: grid;
        min-height: 530px;
        grid-template-columns: minmax(0, 1.02fr) minmax(350px, .98fr);
        align-items: center;
        gap: clamp(2rem, 5vw, 5rem);
        padding: clamp(2rem, 5.5vw, 5rem);
        border: 1px solid #26342f;
        border-radius: 28px;
        background:
            radial-gradient(ellipse at 82% 10%, rgba(108,139,100,.18), transparent 35%),
            linear-gradient(125deg, #121b19 0%, #17231f 60%, #1c2a25 100%);
        box-shadow: 0 28px 75px rgba(27,39,33,.17);
        animation: none;
    }
    .landing-hero:after { display: none; }
    .landing-hero-copy {
        position: relative;
        z-index: 1;
    }
    .landing-kicker {
        display: inline-flex;
        align-items: center;
        gap: .55rem;
        margin: 0 0 1.5rem;
        color: #dfff78;
        font-size: .7rem;
        font-weight: 800;
        letter-spacing: .16em;
    }
    .landing-kicker:before {
        width: 7px;
        height: 7px;
        border-radius: 50%;
        background: #dfff78;
        box-shadow: 0 0 15px rgba(223,255,120,.7);
        content: "";
    }
    .landing-hero h1 {
        max-width: 680px;
        margin: 0;
        color: #f7f8f4;
        font-size: clamp(3.1rem, 5.7vw, 5.7rem);
        font-weight: 760;
        line-height: .98;
        letter-spacing: -.065em;
        text-wrap: balance;
    }
    .landing-hero h1 em {
        color: #dfff78;
        font-style: normal;
    }
    .landing-hero p {
        max-width: 560px;
        margin: 1.45rem 0 0;
        color: #b7c1b9;
        font-size: clamp(1rem, 1.25vw, 1.13rem);
        line-height: 1.75;
    }
    .landing-hero p:hover { transform: none; }
    .landing-visual {
        position: relative;
        min-width: 0;
        aspect-ratio: 1.13;
        overflow: hidden;
        border: 1px solid rgba(224,239,213,.13);
        border-radius: 22px;
        background:
            radial-gradient(circle at 50% 45%, rgba(222,255,120,.08), transparent 56%),
            #192521;
        box-shadow: inset 0 1px 0 rgba(255,255,255,.06), 0 22px 50px rgba(0,0,0,.22);
    }
    .landing-visual:before {
        position: absolute;
        z-index: 1;
        inset: 0;
        background-image: linear-gradient(rgba(220,237,218,.035) 1px, transparent 1px), linear-gradient(90deg, rgba(220,237,218,.035) 1px, transparent 1px);
        background-size: 30px 30px;
        content: "";
        pointer-events: none;
    }
    .landing-visual svg {
        display: block;
        width: 100%;
        height: 100%;
    }
    .landing-detection-label {
        position: absolute;
        z-index: 2;
        top: 13%;
        left: 9%;
        padding: .55rem .7rem;
        border: 1px solid rgba(223,255,120,.28);
        border-radius: 8px;
        background: rgba(15,25,22,.86);
        color: #e7f2db;
        font-size: .62rem;
        font-weight: 750;
        letter-spacing: .1em;
    }
    .landing-detection-label:before {
        display: inline-block;
        width: 6px;
        height: 6px;
        margin-right: .45rem;
        border-radius: 50%;
        background: #dfff78;
        content: "";
    }
    .landing-visual-caption {
        position: absolute;
        z-index: 2;
        right: 5%;
        bottom: 5%;
        left: 5%;
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: .75rem;
        padding: .85rem 1rem;
        border: 1px solid rgba(255,255,255,.1);
        border-radius: 12px;
        background: rgba(15,24,21,.85);
        color: #f5f7f1;
        font-size: .72rem;
    }
    .landing-visual-caption span:last-child {
        color: #dfff78;
        font-size: .65rem;
        font-weight: 750;
        letter-spacing: .08em;
        text-transform: uppercase;
    }
    .landing-cta-row {
        display: flex;
        align-items: center;
        gap: 1.1rem;
        margin: 1.3rem 0 0;
    }
    .landing-cta-note {
        color: #9eaaa1;
        font-size: .79rem;
    }
    .landing-trust-row {
        display: flex;
        flex-wrap: wrap;
        gap: .65rem;
        margin-top: 1.15rem;
    }
    .landing-trust-chip {
        padding: .52rem .75rem;
        border: 1px solid rgba(223,255,120,.17);
        border-radius: 999px;
        background: rgba(223,255,120,.055);
        color: #d4dfd5;
        font-size: .7rem;
        font-weight: 650;
    }
    .landing-content-section {
        padding: clamp(3.5rem, 7vw, 6rem) 0 0;
    }
    .landing-section-heading {
        max-width: 760px;
        margin: 0;
        color: #202722;
        font-size: clamp(2rem, 3.8vw, 3.2rem);
        line-height: 1.08;
        letter-spacing: -.055em;
        text-wrap: balance;
    }
    .landing-section-copy {
        max-width: 650px;
        margin: .85rem 0 1.7rem;
        color: #68716a;
        font-size: 1rem;
        line-height: 1.75;
    }
    .landing-process-grid {
        display: grid;
        grid-template-columns: repeat(3, minmax(0, 1fr));
        gap: 1rem;
        margin-top: 1.7rem;
    }
    .landing-process-card {
        min-height: 210px;
        padding: 1.45rem;
        border: 1px solid #e6e8df;
        border-radius: 18px;
        background: #fff;
        box-shadow: 0 10px 28px rgba(31,40,32,.035);
        transition: transform .2s ease, box-shadow .2s ease, border-color .2s ease;
    }
    .landing-process-card:hover {
        transform: translateY(-4px);
        border-color: #cbd4bd;
        box-shadow: 0 18px 34px rgba(31,40,32,.075);
    }
    .landing-process-number {
        display: grid;
        width: 36px;
        height: 36px;
        place-items: center;
        border-radius: 11px;
        background: #edf4df;
        color: #465438;
        font-size: .76rem;
        font-weight: 850;
    }
    .landing-process-card h3 {
        margin: 1.3rem 0 .45rem;
        color: #202722;
        font-size: 1.12rem;
        letter-spacing: -.025em;
    }
    .landing-process-card p {
        margin: 0;
        color: #69716a;
        font-size: .9rem;
        line-height: 1.65;
    }
    .landing-capability-panel {
        display: grid;
        grid-template-columns: minmax(0, 1fr) minmax(260px, .75fr);
        align-items: center;
        gap: 2rem;
        margin-top: 1.4rem;
        padding: clamp(1.5rem, 4vw, 3rem);
        border: 1px solid #e3e7dd;
        border-radius: 22px;
        background: linear-gradient(135deg, #f0f4e9, #f8f7f2 68%);
    }
    .landing-capability-panel h3 {
        margin: 0 0 .65rem;
        color: #202722;
        font-size: clamp(1.35rem, 2.2vw, 1.8rem);
        letter-spacing: -.04em;
    }
    .landing-capability-panel p {
        max-width: 630px;
        margin: 0;
        color: #68716a;
        line-height: 1.75;
    }
    .landing-capability-list {
        display: grid;
        gap: .7rem;
    }
    .landing-capability-item {
        display: flex;
        align-items: center;
        gap: .75rem;
        padding: .8rem .9rem;
        border: 1px solid rgba(42,58,43,.08);
        border-radius: 12px;
        background: rgba(255,255,255,.75);
        color: #38433b;
        font-size: .84rem;
        font-weight: 650;
    }
    .landing-capability-item b {
        display: grid;
        width: 27px;
        height: 27px;
        flex: 0 0 27px;
        place-items: center;
        border-radius: 9px;
        background: #dfff78;
        color: #253022;
        font-size: .68rem;
    }
    .landing-portal-grid {
        display: grid;
        grid-template-columns: repeat(2, minmax(0, 1fr));
        gap: 1rem;
        margin-top: 1.7rem;
    }
    .landing-portal-card {
        position: relative;
        overflow: hidden;
        min-height: 190px;
        padding: 1.6rem;
        border: 1px solid #e6e8df;
        border-radius: 18px;
        background: #fff;
    }
    .landing-portal-card:after {
        position: absolute;
        right: -25px;
        bottom: -55px;
        width: 150px;
        height: 150px;
        border: 1px solid rgba(119,141,96,.18);
        border-radius: 50%;
        box-shadow: 0 0 0 22px rgba(119,141,96,.045), 0 0 0 44px rgba(119,141,96,.03);
        content: "";
    }
    .landing-portal-label {
        color: #72815f;
        font-size: .68rem;
        font-weight: 800;
        letter-spacing: .13em;
        text-transform: uppercase;
    }
    .landing-portal-card h3 {
        margin: .85rem 0 .45rem;
        color: #202722;
        font-size: 1.25rem;
        letter-spacing: -.035em;
    }
    .landing-portal-card p {
        position: relative;
        z-index: 1;
        max-width: 440px;
        margin: 0;
        color: #69716a;
        font-size: .9rem;
        line-height: 1.7;
    }
    .landing-footer {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 1rem;
        margin-top: clamp(3.5rem, 6vw, 5.5rem);
        padding: 1.4rem 0 .25rem;
        border-top: 1px solid #e4e7df;
        color: #788078;
        font-size: .78rem;
    }
    .landing-footer strong {
        color: #303b32;
        font-weight: 750;
    }
    [data-testid="stButton"] > button {
        min-height: 2.9rem;
        border-radius: 11px;
        font-weight: 700;
    }
    [data-testid="stButton"] > button[kind="primary"] {
        border: 1px solid #dfff78;
        background: #dfff78;
        color: #17211e;
        box-shadow: 0 8px 22px rgba(38,54,30,.13);
    }
    [data-testid="stButton"] > button[kind="primary"]:hover {
        border-color: #c9ef5e;
        background: #c9ef5e;
        color: #17211e;
        box-shadow: 0 11px 26px rgba(38,54,30,.18);
    }
    .st-key-enter_platform [data-testid="stBaseButton-primary"] {
        min-width: 220px;
        min-height: 66px;
        padding: .9rem 1.8rem;
        border-radius: 14px;
        font-size: 1.1rem;
        letter-spacing: -.015em;
    }
    @media (max-width: 900px) {
        .landing-hero {
            min-height: auto;
            grid-template-columns: 1fr;
            gap: 2.25rem;
        }
        .landing-visual { max-width: 680px; width: 100%; margin: 0 auto; }
        .landing-capability-panel { grid-template-columns: 1fr; }
    }
    @media (max-width: 680px) {
        [data-testid="stMainBlockContainer"] { padding: .8rem 1rem 2.5rem; }
        .landing-shell { padding-top: .2rem; }
        .landing-nav { margin-bottom: .85rem; }
        .landing-nav-label { padding: .43rem .62rem; font-size: .64rem; }
        .landing-hero {
            gap: 1.7rem;
            padding: 2rem 1.4rem;
            border-radius: 21px;
        }
        .landing-hero h1 { font-size: clamp(2.85rem, 11vw, 4.5rem); }
        .landing-hero p { font-size: .97rem; }
        .landing-visual { border-radius: 17px; }
        .landing-content-section { padding-top: 3.5rem; }
        .landing-process-grid, .landing-portal-grid { grid-template-columns: 1fr; }
        .landing-process-card { min-height: auto; }
        .landing-footer { align-items: flex-start; flex-direction: column; }
    }
    @media (prefers-reduced-motion: reduce) {
        .landing-process-card { transition: none; }
    }
    .st-key-portal_screen {
        max-width: 1180px;
        margin: 0 auto;
    }
    .portal-back-row {
        margin: 0 0 1rem;
    }
    .portal-intro {
        position: relative;
        overflow: hidden;
        margin-bottom: 1.8rem;
        padding: clamp(1.7rem, 4vw, 3rem);
        border: 1px solid #26342f;
        border-radius: 22px;
        background:
            radial-gradient(circle at 90% 15%, rgba(223,255,120,.11), transparent 18rem),
            linear-gradient(125deg, #121b19, #1d2b25);
        color: #f7f8f4;
    }
    .portal-intro:after {
        position: absolute;
        top: -90px;
        right: -25px;
        width: 240px;
        height: 240px;
        border: 1px solid rgba(223,255,120,.18);
        border-radius: 50%;
        box-shadow: 0 0 0 28px rgba(223,255,120,.035), 0 0 0 56px rgba(223,255,120,.025);
        content: "";
        pointer-events: none;
    }
    .portal-intro-kicker {
        position: relative;
        z-index: 1;
        margin-bottom: .65rem;
        color: #dfff78;
        font-size: .68rem;
        font-weight: 800;
        letter-spacing: .15em;
        text-transform: uppercase;
    }
    .portal-intro h1 {
        position: relative;
        z-index: 1;
        margin: 0;
        color: #f7f8f4;
        font-size: clamp(2.2rem, 4.5vw, 3.5rem);
        line-height: 1.04;
        letter-spacing: -.055em;
    }
    .portal-intro p {
        position: relative;
        z-index: 1;
        max-width: 650px;
        margin: .8rem 0 0;
        color: #bbc6bd;
        font-size: 1rem;
        line-height: 1.7;
    }
    .portal-card-heading {
        display: flex;
        align-items: flex-start;
        gap: 1rem;
        margin-bottom: .8rem;
    }
    .portal-card-icon {
        position: relative;
        display: grid;
        width: 48px;
        height: 48px;
        flex: 0 0 48px;
        place-items: center;
        border-radius: 14px;
        background: #edf4df;
        color: #384b32;
        box-shadow: inset 0 0 0 1px rgba(111, 143, 82, .12);
        transition: transform .35s cubic-bezier(.2, .8, .2, 1), box-shadow .35s ease;
    }
    .portal-card-icon svg {
        width: 28px;
        height: 28px;
        overflow: visible;
        stroke: currentColor;
        stroke-linecap: round;
        stroke-linejoin: round;
        stroke-width: 1.8;
    }
    .portal-card-icon.citizen svg {
        animation: premiumFloat 4.5s ease-in-out infinite;
    }
    .portal-card-icon.authority {
        background: #e7eefb;
        color: #38527d;
    }
    .portal-card-icon.authority svg {
        animation: premiumFloat 5.2s ease-in-out infinite reverse;
    }
    .st-key-portal_screen [data-testid="stVerticalBlockBorderWrapper"]:hover .portal-card-icon {
        transform: translateY(-4px) rotate(-3deg) scale(1.08);
        box-shadow: 0 10px 20px rgba(58, 84, 55, .16), inset 0 0 0 1px rgba(111, 143, 82, .2);
    }
    .portal-card-eyebrow {
        margin: .15rem 0 .25rem;
        color: #748064;
        font-size: .66rem;
        font-weight: 800;
        letter-spacing: .13em;
        text-transform: uppercase;
    }
    .portal-card-heading h2 {
        margin: 0;
        color: #202722;
        font-size: 1.38rem;
        letter-spacing: -.04em;
    }
    .portal-card-copy {
        min-height: 3.3rem;
        margin: 0 0 1.1rem;
        color: #69716a;
        font-size: .91rem;
        line-height: 1.7;
    }
    .st-key-portal_screen [data-testid="stVerticalBlockBorderWrapper"] {
        min-height: 100%;
        padding: 1.35rem;
        border: 1px solid #e4e8df;
        border-radius: 18px;
        background: #fff;
        box-shadow: 0 12px 32px rgba(31,40,32,.045);
    }
    .st-key-portal_screen [data-testid="stForm"] {
        padding: 1rem;
        border: 1px solid #e8ebe4;
        border-radius: 14px;
        background: #fafbf8;
    }
    .st-key-portal_screen [data-testid="stTextInput"] input {
        min-height: 2.8rem;
        border-radius: 9px;
    }
    .st-key-portal_screen [data-testid="stFormSubmitButton"] > button {
        min-height: 2.9rem;
        border-radius: 10px;
        font-weight: 700;
    }
    .st-key-authority_login_form {
        padding: 1.15rem !important;
        border: 1px solid #e3e8de !important;
        border-radius: 15px !important;
        background: linear-gradient(145deg, #fbfcf8, #f3f6ed) !important;
    }
    .st-key-authority_login_form [data-testid="stTextInput"] label,
    .st-key-authority_otp_form [data-testid="stTextInput"] label {
        color: #485548;
        font-size: .79rem;
        font-weight: 700;
    }
    .st-key-authority_login_form [data-testid="stTextInput"] input,
    .st-key-authority_otp_form [data-testid="stTextInput"] input {
        min-height: 3rem;
        border: 1px solid #dfe5da;
        border-radius: 10px;
        background: #fff;
    }
    .st-key-authority_login_form [data-testid="stFormSubmitButton"] > button,
    .st-key-authority_otp_form [data-testid="stFormSubmitButton"] > button {
        min-height: 3rem;
        border: 1px solid #dfff78;
        border-radius: 10px;
        background: #dfff78;
        color: #17211e;
        font-weight: 750;
        transition: transform .18s ease, box-shadow .18s ease, background .18s ease;
    }
    .st-key-authority_login_form [data-testid="stFormSubmitButton"] > button:hover,
    .st-key-authority_otp_form [data-testid="stFormSubmitButton"] > button:hover {
        transform: translateY(-1px);
        border-color: #c9ef5e;
        background: #c9ef5e;
        box-shadow: 0 8px 20px rgba(38,54,30,.12);
        color: #17211e;
    }
    .st-key-portal_screen [data-testid="stButton"] > button {
        min-height: 3rem;
        border-radius: 10px;
        font-weight: 700;
    }
    .st-key-login_back_button [data-testid="stBaseButton-secondary"] {
        min-height: 2.6rem;
        border-radius: 9px;
        color: #4a554c;
    }
    /* Premium workspace system */
    .stApp {
        background:
            radial-gradient(circle at 8% 0%, rgba(223,255,120,.12), transparent 25rem),
            linear-gradient(135deg, #f8faf5 0%, #f5f7f1 48%, #eef3e8 100%);
    }
    [data-testid="stHeader"] { background: rgba(248,250,245,.78); }
    [data-testid="stMain"] { padding-top: 1.5rem; }
    [data-testid="stSidebar"] {
        border-right: 1px solid rgba(30,48,38,.12);
        background: linear-gradient(180deg, #18241f 0%, #22342b 58%, #1b2a24 100%);
    }
    [data-testid="stSidebar"] * { color: #eef5e9; }
    [data-testid="stSidebar"] hr { border-color: rgba(223,255,120,.18); }
    [data-testid="stSidebar"] [data-testid="stRadio"] label {
        margin: .25rem 0;
        padding: .7rem .8rem;
        border: 1px solid transparent;
        border-radius: 11px;
        transition: background .2s ease, border-color .2s ease, transform .2s ease;
    }
    [data-testid="stSidebar"] [data-testid="stRadio"] label:hover {
        transform: translateX(3px);
        border-color: rgba(223,255,120,.3);
        background: rgba(223,255,120,.1);
    }
    [data-testid="stSidebar"] [data-testid="stRadio"] label[data-checked="true"] {
        border-color: rgba(223,255,120,.52);
        background: linear-gradient(90deg, rgba(223,255,120,.22), rgba(223,255,120,.06));
    }
    .workspace-page-hero {
        position: relative;
        overflow: hidden;
        margin: .2rem 0 1.5rem;
        padding: 1.8rem 2rem;
        border: 1px solid rgba(42,65,52,.13);
        border-radius: 22px;
        background: linear-gradient(125deg, #1a2922 0%, #294235 70%, #536b3f 100%);
        box-shadow: 0 18px 38px rgba(28,48,37,.12);
        color: #f5faef;
    }
    .workspace-page-hero:before {
        position: absolute;
        left: -12%;
        top: 0;
        width: 22%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(223,255,120,.16), transparent);
        content: "";
        pointer-events: none;
        animation: scanLine 8s ease-in-out infinite;
    }
    .hero-pothole-scan {
        position: absolute;
        right: 12%;
        bottom: 17%;
        width: 3.2rem;
        height: 1.55rem;
        border: 2px solid rgba(223,255,120,.5);
        border-radius: 50%;
        transform: rotate(-12deg);
        animation: potholePulse 3.8s ease-in-out infinite;
    }
    .hero-pothole-scan:before {
        position: absolute;
        left: 50%;
        top: -1.4rem;
        width: 1px;
        height: 1.3rem;
        background: rgba(223,255,120,.5);
        content: "";
    }
    .hero-pothole-scan:after {
        position: absolute;
        left: 50%;
        top: -2rem;
        color: rgba(223,255,120,.68);
        content: "YOLO";
        font-size: .52rem;
        font-weight: 850;
        letter-spacing: .16em;
        transform: translateX(-50%);
    }
    .workspace-page-brand {
        position: relative;
        z-index: 1;
        display: flex;
        align-items: center;
        gap: .55rem;
        margin-bottom: 1.2rem;
        color: #dfff78;
        font-size: .78rem;
        font-weight: 850;
        letter-spacing: .16em;
        text-transform: uppercase;
    }
    .workspace-page-brand-mark {
        display: inline-grid;
        width: 2rem;
        height: 2rem;
        place-items: center;
        border: 1px solid rgba(223,255,120,.5);
        border-radius: 9px;
        background: rgba(223,255,120,.14);
        color: #fff;
        font-size: .72rem;
        letter-spacing: -.05em;
    }
    .workspace-page-hero:after {
        position: absolute;
        right: -40px;
        top: -90px;
        width: 250px;
        height: 250px;
        border: 1px solid rgba(223,255,120,.22);
        border-radius: 50%;
        box-shadow: 0 0 0 28px rgba(223,255,120,.06), 0 0 0 58px rgba(223,255,120,.035);
        content: "";
    }
    .workspace-page-kicker {
        position: relative;
        z-index: 1;
        margin-bottom: .45rem;
        color: #dfff78;
        font-size: .68rem;
        font-weight: 800;
        letter-spacing: .16em;
        text-transform: uppercase;
    }
    .workspace-page-hero h1 {
        position: relative;
        z-index: 1;
        margin: 0;
        color: #fff;
        font-size: clamp(2rem, 4vw, 3.25rem);
        letter-spacing: -.055em;
    }
    .workspace-page-hero p {
        position: relative;
        z-index: 1;
        max-width: 720px;
        margin: .65rem 0 0;
        color: #c8d6c9;
        line-height: 1.6;
    }
    .workspace-page-trail {
        position: relative;
        z-index: 1;
        display: flex;
        flex-wrap: wrap;
        gap: .55rem;
        margin-top: 1.15rem;
    }
    .workspace-page-trail span {
        padding: .38rem .68rem;
        border: 1px solid rgba(223,255,120,.25);
        border-radius: 999px;
        background: rgba(223,255,120,.09);
        color: #e9f4dc;
        font-size: .72rem;
        font-weight: 700;
    }
    [data-testid="stVerticalBlockBorderWrapper"] {
        border-color: rgba(42,65,52,.13);
        border-radius: 18px;
        background: rgba(255,255,255,.72);
        box-shadow: 0 10px 28px rgba(37,54,42,.055);
    }
    [data-testid="stMetric"] {
        padding: 1rem 1.05rem;
        border: 1px solid rgba(42,65,52,.11);
        border-radius: 15px;
        background: rgba(255,255,255,.78);
        box-shadow: 0 8px 20px rgba(37,54,42,.05);
    }
    [data-testid="stMetricLabel"] { color: #667568; font-weight: 700; }
    [data-testid="stMetricValue"] { color: #20372a; letter-spacing: -.04em; }
    [data-testid="stDataFrame"] {
        overflow: hidden;
        border: 1px solid rgba(42,65,52,.14);
        border-radius: 16px;
        box-shadow: 0 10px 24px rgba(37,54,42,.06);
    }
    [data-testid="stFileUploader"], [data-testid="stTextInput"], [data-testid="stTextArea"], [data-testid="stSelectbox"] {
        border-radius: 12px;
    }
    .stButton > button, [data-testid="stFormSubmitButton"] > button {
        border-radius: 11px;
        border: 1px solid #b8d84f;
        font-weight: 750;
        transition: transform .18s ease, box-shadow .18s ease, filter .18s ease;
    }
    .stButton > button:hover, [data-testid="stFormSubmitButton"] > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 22px rgba(78,106,42,.18);
        filter: brightness(1.02);
    }
    .page-section-label {
        margin: 1.4rem 0 .65rem;
        color: #526457;
        font-size: .72rem;
        font-weight: 800;
        letter-spacing: .14em;
        text-transform: uppercase;
    }
    @media (max-width: 680px) {
        .tech-watermark { right: 1rem; bottom: .7rem; font-size: .5rem; }
        .pothole-orbit { left: auto; right: 1rem; bottom: 2.8rem; }
        .hero-pothole-scan { right: 8%; opacity: .65; }
        .portal-intro { padding: 1.6rem 1.35rem; border-radius: 18px; }
        .portal-card-copy { min-height: auto; }
        .st-key-portal_screen [data-testid="stVerticalBlockBorderWrapper"] { padding: 1.1rem; }
    }

    /* Keep application surfaces crisp and opaque so content never sits on a
       distracting translucent layer. Decorative transparency remains limited
       to hero artwork and status accents. */
    html, body, [data-testid="stAppViewContainer"], [data-testid="stMain"] {
        background: #f3f6ef !important;
    }
    .stApp {
        background:
            radial-gradient(circle at 8% 0%, rgba(223,255,120,.1), transparent 25rem),
            linear-gradient(135deg, #f8faf5 0%, #f3f6ef 52%, #eaf1e4 100%) !important;
    }
    [data-testid="stHeader"] {
        background: #f3f6ef !important;
        border-bottom: 1px solid #e1e8dc;
    }
    [data-testid="stVerticalBlockBorderWrapper"],
    [data-testid="stMetric"],
    [data-testid="stDataFrame"],
    [data-testid="stTable"] {
        background: #ffffff !important;
        backdrop-filter: none !important;
    }
    [data-testid="stVerticalBlockBorderWrapper"] {
        border-color: #dce5d8 !important;
        box-shadow: 0 12px 30px rgba(37,54,42,.07) !important;
    }
    [data-testid="stMetric"] {
        border-color: #dce5d8 !important;
        box-shadow: 0 8px 22px rgba(37,54,42,.06) !important;
    }
    [data-testid="stTextInput"] input,
    [data-testid="stTextArea"] textarea,
    [data-testid="stSelectbox"] [role="combobox"],
    [data-testid="stFileUploader"] section {
        background: #ffffff !important;
        border-color: #d6e0d1 !important;
    }
    [data-testid="stFileUploader"] section {
        box-shadow: inset 0 0 0 1px #edf2e9;
    }
    .landing-card,
    .landing-availability-copy,
    .landing-capability-item {
        background: #ffffff !important;
    }
    :root {
        --premium-ink: #17211d;
        --premium-muted: #68756b;
        --premium-lime: #dfff78;
        --premium-border: #dbe5d8;
        --premium-surface: #ffffff;
        --premium-surface-soft: #f7faf4;
        --premium-shadow: 0 16px 38px rgba(31, 52, 38, .08);
    }
    html, body, [class*="css"], button, input, textarea, select {
        font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }
    [data-testid="stMainBlockContainer"] {
        position: relative;
        z-index: 1;
    }
    [data-testid="stMainBlockContainer"]::before {
        position: fixed;
        z-index: -1;
        top: 0;
        right: 0;
        width: 42vw;
        height: 42vw;
        max-width: 620px;
        max-height: 620px;
        border: 1px solid rgba(142, 175, 115, .12);
        border-radius: 50%;
        box-shadow: 0 0 0 34px rgba(142, 175, 115, .035), 0 0 0 68px rgba(142, 175, 115, .025);
        content: "";
        pointer-events: none;
    }
    [data-testid="stHeader"] {
        min-height: 3.8rem;
        box-shadow: 0 1px 0 #e1e8dc;
    }
    [data-testid="stSidebar"] {
        box-shadow: 8px 0 30px rgba(25, 45, 32, .12);
    }
    [data-testid="stSidebar"] [data-testid="stAlert"] {
        border: 1px solid rgba(183, 221, 175, .55) !important;
        background: #eaf7e7 !important;
        color: #23452b !important;
        box-shadow: 0 8px 18px rgba(8, 24, 15, .12) !important;
    }
    [data-testid="stSidebar"] [data-testid="stAlert"] * {
        color: #23452b !important;
    }
    [data-testid="stSidebar"] [data-testid="stAlert"] svg {
        fill: #36a269 !important;
        color: #36a269 !important;
    }
    [data-testid="stSidebar"] .stButton > button {
        border: 1px solid rgba(223, 255, 120, .4) !important;
        background: #263d31 !important;
        color: #f4faef !important;
        box-shadow: 0 8px 18px rgba(8, 24, 15, .14) !important;
    }
    [data-testid="stSidebar"] .stButton > button:hover {
        border-color: #dfff78 !important;
        background: #304c3b !important;
        color: #ffffff !important;
    }
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h1,
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h2,
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h3 {
        letter-spacing: -.04em;
    }
    [data-testid="stVerticalBlockBorderWrapper"],
    [data-testid="stMetric"],
    [data-testid="stDataFrame"],
    [data-testid="stTable"],
    .st-key-portal_screen [data-testid="stForm"] {
        background: var(--premium-surface) !important;
        border: 1px solid var(--premium-border) !important;
        box-shadow: var(--premium-shadow) !important;
    }
    [data-testid="stVerticalBlockBorderWrapper"]:hover,
    [data-testid="stMetric"]:hover {
        border-color: #b9cfab !important;
        box-shadow: 0 20px 44px rgba(31, 52, 38, .12) !important;
    }
    [data-testid="stMetric"] {
        transition: border-color .2s ease, box-shadow .2s ease, transform .2s ease;
    }
    [data-testid="stMetric"]:hover {
        transform: translateY(-2px);
    }
    [data-testid="stMetricLabel"] {
        color: var(--premium-muted) !important;
        font-size: .73rem !important;
        font-weight: 800 !important;
        letter-spacing: .08em;
        text-transform: uppercase;
    }
    [data-testid="stMetricValue"] {
        color: var(--premium-ink) !important;
        font-weight: 800 !important;
    }
    [data-testid="stTextInput"] input,
    [data-testid="stTextArea"] textarea,
    [data-testid="stSelectbox"] [role="combobox"],
    [data-testid="stNumberInput"] input,
    [data-testid="stFileUploader"] section {
        min-height: 2.85rem;
        border: 1px solid #d5e0d1 !important;
        border-radius: 12px !important;
        background: #fff !important;
        color: var(--premium-ink) !important;
        box-shadow: inset 0 1px 2px rgba(33, 54, 39, .03);
        transition: border-color .18s ease, box-shadow .18s ease;
    }
    [data-testid="stTextInput"] input:focus,
    [data-testid="stTextArea"] textarea:focus,
    [data-testid="stNumberInput"] input:focus {
        border-color: #a4c67f !important;
        box-shadow: 0 0 0 3px rgba(164, 198, 127, .2) !important;
        outline: none;
    }
    [data-testid="stFileUploader"] section {
        display: grid;
        min-height: 8rem;
        place-items: center;
        border-style: dashed !important;
        background: var(--premium-surface-soft) !important;
    }
    [data-testid="stFileUploader"] section:hover {
        border-color: #9cbd78 !important;
        background: #f1f8e9 !important;
    }
    .stButton > button,
    [data-testid="stFormSubmitButton"] > button,
    [data-testid="stDownloadButton"] > button {
        min-height: 2.85rem;
        padding: .55rem 1rem;
        border-radius: 11px !important;
        border: 1px solid #c8d9bc !important;
        background: #fff !important;
        color: var(--premium-ink) !important;
        font-weight: 750 !important;
        letter-spacing: -.01em;
        box-shadow: 0 5px 14px rgba(36, 58, 42, .06);
    }
    .stButton > button:hover,
    [data-testid="stFormSubmitButton"] > button:hover,
    [data-testid="stDownloadButton"] > button:hover {
        border-color: #a7c77f !important;
        background: #f5faef !important;
        box-shadow: 0 10px 24px rgba(62, 92, 48, .13);
        transform: translateY(-2px);
    }
    .stButton > button[kind="primary"],
    [data-testid="stFormSubmitButton"] > button[kind="primary"] {
        border-color: #c9ef5e !important;
        background: var(--premium-lime) !important;
        color: #17211e !important;
        box-shadow: 0 8px 20px rgba(143, 177, 69, .18);
    }
    .stButton > button[kind="primary"]:hover,
    [data-testid="stFormSubmitButton"] > button[kind="primary"]:hover {
        background: #d2f66d !important;
        box-shadow: 0 12px 28px rgba(143, 177, 69, .25);
    }
    [data-testid="stAlert"] {
        border: 1px solid #dce8d4 !important;
        border-radius: 14px !important;
        background: #fbfdf9 !important;
        box-shadow: 0 8px 20px rgba(37, 54, 42, .05);
    }
    [data-testid="stExpander"] {
        overflow: hidden;
        border: 1px solid var(--premium-border) !important;
        border-radius: 14px !important;
        background: #fff !important;
    }
    [data-testid="stExpander"] summary:hover {
        background: #f7faf4 !important;
    }
    [data-testid="stTabs"] [role="tablist"] {
        gap: .35rem;
        border-bottom: 1px solid var(--premium-border);
    }
    [data-testid="stTabs"] button[role="tab"] {
        padding: .7rem 1rem;
        border-radius: 10px 10px 0 0;
        color: var(--premium-muted);
        font-weight: 750;
    }
    [data-testid="stTabs"] button[role="tab"][aria-selected="true"] {
        color: var(--premium-ink);
        background: #f1f8e9;
    }
    [data-testid="stDataFrame"] {
        box-shadow: 0 12px 28px rgba(37, 54, 42, .07) !important;
    }
    .workspace-page-hero {
        box-shadow: 0 22px 48px rgba(28, 48, 37, .16);
    }
    .landing-process-card,
    .landing-portal-card {
        box-shadow: 0 14px 34px rgba(31, 52, 38, .07);
    }
    .landing-process-card:hover,
    .landing-portal-card:hover {
        border-color: #b9cfab;
        box-shadow: 0 22px 44px rgba(31, 52, 38, .13);
        transform: translateY(-5px);
    }
    @keyframes premiumReveal {
        from { opacity: 0; transform: translateY(18px) scale(.985); }
        to { opacity: 1; transform: translateY(0) scale(1); }
    }
    @keyframes premiumFloat {
        0%, 100% { transform: translate3d(0, 0, 0) rotate(0deg); }
        50% { transform: translate3d(0, -9px, 0) rotate(1deg); }
    }
    @keyframes premiumGlow {
        0%, 100% { opacity: .35; transform: scale(.96); }
        50% { opacity: .8; transform: scale(1.04); }
    }
    @keyframes premiumShimmer {
        0% { transform: translateX(-140%) skewX(-18deg); }
        55%, 100% { transform: translateX(180%) skewX(-18deg); }
    }
    .animated-element,
    .workspace-page-hero,
    .portal-intro,
    .landing-content-section {
        animation: premiumReveal .72s cubic-bezier(.2, .75, .25, 1) both;
    }
    .workspace-page-hero {
        isolation: isolate;
        transform-style: preserve-3d;
        transition: transform .45s cubic-bezier(.2, .8, .2, 1), box-shadow .45s ease;
    }
    .workspace-page-hero:hover {
        transform: perspective(1100px) rotateX(1deg) translateY(-3px);
        box-shadow: 0 30px 60px rgba(28, 48, 37, .2);
    }
    .workspace-page-hero:after {
        animation: premiumGlow 5s ease-in-out infinite;
        transform-origin: center;
    }
    .workspace-page-brand-mark {
        animation: premiumFloat 5s ease-in-out infinite;
    }
    .landing-visual {
        transform: perspective(1000px) rotateY(-2deg);
        transition: transform .55s cubic-bezier(.2, .8, .2, 1), box-shadow .55s ease;
    }
    .landing-visual:hover {
        transform: perspective(1000px) rotateY(0deg) rotateX(1deg) translateY(-5px);
        box-shadow: inset 0 1px 0 rgba(255,255,255,.08), 0 30px 64px rgba(0,0,0,.28);
    }
    .landing-visual:after {
        position: absolute;
        z-index: 3;
        top: 0;
        bottom: 0;
        left: 0;
        width: 22%;
        background: linear-gradient(90deg, transparent, rgba(223,255,120,.16), transparent);
        content: "";
        pointer-events: none;
        animation: premiumShimmer 7s ease-in-out infinite;
    }
    .landing-process-card,
    .landing-portal-card,
    [data-testid="stVerticalBlockBorderWrapper"],
    [data-testid="stMetric"] {
        transform-style: preserve-3d;
        transition: transform .35s cubic-bezier(.2, .8, .2, 1), box-shadow .35s ease, border-color .35s ease;
    }
    .landing-process-card:hover,
    .landing-portal-card:hover,
    [data-testid="stVerticalBlockBorderWrapper"]:hover {
        transform: perspective(1000px) translateY(-6px) rotateX(1deg);
    }
    [data-testid="stMetric"]:hover {
        transform: perspective(900px) translateY(-4px) rotateX(2deg);
    }
    .stButton > button,
    [data-testid="stFormSubmitButton"] > button,
    [data-testid="stDownloadButton"] > button {
        position: relative;
        overflow: hidden;
        transition: transform .25s cubic-bezier(.2, .8, .2, 1), box-shadow .25s ease, background .25s ease !important;
    }
    .stButton > button::after,
    [data-testid="stFormSubmitButton"] > button::after,
    [data-testid="stDownloadButton"] > button::after {
        position: absolute;
        top: -30%;
        bottom: -30%;
        left: -45%;
        width: 20%;
        background: rgba(255,255,255,.45);
        content: "";
        transform: skewX(-18deg);
        transition: none;
    }
    .stButton > button:hover::after,
    [data-testid="stFormSubmitButton"] > button:hover::after,
    [data-testid="stDownloadButton"] > button:hover::after {
        animation: premiumShimmer .8s ease-out;
    }
    [data-testid="stSidebar"] [data-testid="stRadio"] label {
        transition: transform .28s cubic-bezier(.2, .8, .2, 1), background .28s ease, border-color .28s ease !important;
    }
    [data-testid="stSidebar"] [data-testid="stRadio"] label:hover {
        transform: translateX(6px) scale(1.01) !important;
    }
    @media (prefers-reduced-motion: reduce) {
        .animated-element,
        .workspace-page-hero,
        .portal-intro,
        .landing-content-section,
        .workspace-page-brand-mark,
        .landing-visual,
        .landing-visual:after {
            animation: none !important;
            transform: none !important;
        }
        *, *::before, *::after {
            transition-duration: .01ms !important;
        }
    }
    @media (max-width: 760px) {
        [data-testid="stMainBlockContainer"]::before { display: none; }
        [data-testid="stVerticalBlockBorderWrapper"] { border-radius: 14px !important; }
        .landing-process-grid,
        .landing-portal-grid,
        .landing-capability-panel { grid-template-columns: 1fr; }
    }
</style>
""", unsafe_allow_html=True)

st.markdown(
    """
    <div class="tech-watermark" aria-hidden="true">
        <span>DEEP LEARNING</span><span>YOLO VISION</span>
    </div>
    <div class="pothole-orbit" aria-hidden="true"></div>
    """,
    unsafe_allow_html=True,
)


# --- Core Logic Functions ---
@st.cache_data(ttl=300, show_spinner=False)
def geocode_manual_address(address: str):
    if not address or not address.strip():
        return None, None
    url = "https://nominatim.openstreetmap.org/search"
    headers = {"User-Agent": "Pothole-Detection-Hackathon-Client"}
    params = {"q": address.strip(), "format": "json", "limit": 1}
    try:
        res = requests.get(url, headers=headers, params=params, timeout=5)
        if res.status_code == 200:
            data = res.json()
            if data:
                return float(data[0]["lat"]), float(data[0]["lon"])
    except Exception:
        pass
    return None, None

@st.cache_data(ttl=5, show_spinner=False)
def fetch_defects():
    try:
        response = requests.get(f"{BACKEND_BASE_URL}/api/geo/defects", timeout=3)
        if response.status_code == 200:
            return response.json().get("defects", [])
    except requests.RequestException:
        pass
    return []

@st.cache_data(ttl=5, show_spinner=False)
def fetch_authority_complaints(access_token):
    if not access_token:
        return []
    try:
        headers = {"Authorization": "Bearer " + access_token}
        response = requests.get(
            f"{BACKEND_BASE_URL}/api/authority/complaints",
            headers=headers,
            timeout=10,
        )
        if response.status_code == 200:
            return response.json().get("complaints", [])
        if response.status_code == 401:
            st.session_state.pop("staff_session", None)
            st.session_state["user_role"] = None
            clear_workspace_session()
        else:
            st.error(response_detail(response, "Could not load authority complaints."))
    except requests.RequestException as error:
        st.error(f"Backend unavailable: {error}")
    return []

def dashboard_records_for_session(authority_complaints, defects, session):
    return authority_complaints if session else defects

def is_active_complaint(complaint):
    return complaint.get("status") not in {"RESOLVED", "REJECTED"}

@st.cache_data(ttl=5, show_spinner=False)
def backend_is_available():
    try:
        return requests.get(f"{BACKEND_BASE_URL}/api/geo/defects", timeout=2).status_code == 200
    except requests.RequestException:
        return False

def render_dynamic_map(lat=None, lon=None, label="Reported Location", height=520):
    if lat is not None and lon is not None:
        leaflet_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
            <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
            <style>
                html, body, #map {{ height: 100%; width: 100%; margin: 0; padding: 0; border-radius: 8px; overflow: hidden; }}
            </style>
        </head>
        <body>
            <div id="map"></div>
            <script>
                const map = L.map('map').setView([{lat}, {lon}], 16);
                L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
                    attribution: '&copy; OpenStreetMap contributors'
                }}).addTo(map);
                L.marker([{lat}, {lon}]).addTo(map)
                    .bindPopup('<b style="font-family:sans-serif;">{label}</b><br>Lat: {lat:.5f}, Lon: {lon:.5f}')
                    .openPopup();
            </script>
        </body>
        </html>
        """
        components.html(leaflet_html, height=height)
    elif os.path.exists("dispatch_map.html"):
        with open("dispatch_map.html", "r", encoding="utf-8") as map_file:
            components.html(map_file.read(), height=height)
    else:
        st.info("📍 Map Data Unavailable. Dispatch a report to populate the city map.")

def render_preview(media):
    extension = media.name.rsplit(".", 1)[-1].lower()
    if extension in VIDEO_TYPES:
        st.video(media)
        return "video"
    st.image(Image.open(media), caption=media.name, use_container_width=True)
    return "image"

def analyze_uploaded_media(media, latitude, longitude, manual_address, pincode, severity, reporter_phone, reporter_email):
    files = {
        "media": (media.name, media.getvalue(), media.type or "application/octet-stream")
    }
    data = {"severity": severity, "manual_address": manual_address, "pincode": pincode, "reporter_phone": reporter_phone, "reporter_email": reporter_email}
    if latitude is not None and longitude is not None:
        data.update({"latitude": latitude, "longitude": longitude})
    return requests.post(
        f"{BACKEND_BASE_URL}/api/report/analyze",
        files=files,
        data=data,
        timeout=300,
    )

def api_request(method, path, **kwargs):
    try:
        return requests.request(method, f"{BACKEND_BASE_URL}{path}", timeout=10, **kwargs)
    except requests.RequestException as error:
        st.error(f"Backend unavailable: {error}")
        return None


def response_detail(response, fallback: str) -> str:
    try:
        payload = response.json()
    except ValueError:
        return fallback
    return payload.get("detail", fallback) if isinstance(payload, dict) else fallback


# --- Session Management ---
browser_cookies = st.context.cookies
saved_role = browser_cookies.get(ROLE_COOKIE)
saved_token = browser_cookies.get(TOKEN_COOKIE)
saved_account = browser_cookies.get(ACCOUNT_COOKIE)
if st.session_state.get("user_role") is None:
    if saved_role == "authority" and saved_token:
        st.session_state["user_role"] = "authority"
        st.session_state["staff_session"] = {
            "access_token": saved_token,
            "role": "authority",
            "account_id": saved_account,
        }
    elif saved_role == "citizen":
        st.session_state["user_role"] = "citizen"
    else:
        st.session_state["user_role"] = None
if "show_landing" not in st.session_state:
    st.session_state["show_landing"] = st.session_state["user_role"] is None


def persist_workspace_session(role: str, session: dict | None = None):
    cookie_controller.set(ROLE_COOKIE, role, max_age=SESSION_COOKIE_MAX_AGE)
    if session and session.get("access_token"):
        cookie_controller.set(TOKEN_COOKIE, session["access_token"], max_age=SESSION_COOKIE_MAX_AGE)
        cookie_controller.set(ACCOUNT_COOKIE, str(session.get("account_id", "")), max_age=SESSION_COOKIE_MAX_AGE)
    else:
        for cookie_name in (TOKEN_COOKIE, ACCOUNT_COOKIE):
            if cookie_controller.get(cookie_name) is not None:
                cookie_controller.remove(cookie_name)


def clear_workspace_session():
    for cookie_name in (ROLE_COOKIE, TOKEN_COOKIE, ACCOUNT_COOKIE):
        if cookie_controller.get(cookie_name) is not None:
            cookie_controller.remove(cookie_name)


def render_workspace_hero(kicker, title, description):
    st.markdown(
        f"""
        <section class="workspace-page-hero animated-element">
            <div class="hero-pothole-scan" aria-hidden="true"></div>
            <div class="workspace-page-brand">
                <span class="workspace-page-brand-mark">PD</span>
                <span>Pothole Detection</span>
            </div>
            <div class="workspace-page-kicker">{kicker}</div>
            <h1>{title}</h1>
            <p>{description}</p>
            <div class="workspace-page-trail">
                <span>● Deep learning</span>
                <span>⌖ YOLO detection</span>
                <span>✦ Human reviewed</span>
            </div>
        </section>
        """,
        unsafe_allow_html=True,
    )


# --- Public Landing Page ---
def render_landing_page():
    st.markdown("""
    <div class="landing-shell animated-element">
        <header class="landing-nav">
            <span class="landing-brand-mark" aria-hidden="true">PD</span>
            <span class="landing-brand-name">Pothole Detection</span>
            <span class="landing-nav-label">Pothole intelligence for safer streets</span>
        </header>
        <section class="landing-hero">
            <div class="landing-hero-copy">
                <div class="landing-kicker">POTHOLE DETECTION · DEEP LEARNING</div>
                <h1>See the road.<br>Spot the risk.<br><em>Move to repair.</em></h1>
                <p>Turn road photos and video into clear pothole detections, useful severity estimates, and location-aware reports.</p>
                <div class="landing-trust-row">
                    <span class="landing-trust-chip">YOLO object detection</span>
                    <span class="landing-trust-chip">Photos + video</span>
                    <span class="landing-trust-chip">Annotated results</span>
                </div>
            </div>
            <div class="landing-visual" role="img" aria-label="Illustration of deep-learning pothole detection on a road">
                <span class="landing-detection-label">POTHOLE DETECTED</span>
                <svg viewBox="0 0 640 560" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
                    <defs>
                        <linearGradient id="road-surface" x1="0" y1="0" x2="0.8" y2="1">
                            <stop offset="0" stop-color="#394943"/>
                            <stop offset="1" stop-color="#202d28"/>
                        </linearGradient>
                        <linearGradient id="road-glow" x1="0" y1="0" x2="1" y2="1">
                            <stop offset="0" stop-color="#dfff78" stop-opacity=".16"/>
                            <stop offset="1" stop-color="#dfff78" stop-opacity="0"/>
                        </linearGradient>
                        <filter id="soft-shadow" x="-30%" y="-30%" width="160%" height="160%">
                            <feGaussianBlur stdDeviation="13"/>
                        </filter>
                    </defs>
                    <path d="M0 0h640v560H0z" fill="#192521"/>
                    <path d="M87 560 220 65h201l132 495z" fill="url(#road-surface)"/>
                    <path d="m87 560 133-495h25L150 560z" fill="#50615a" opacity=".32"/>
                    <path d="m553 560-132-495h-25l95 495z" fill="#101a17" opacity=".42"/>
                    <path d="m320 110 4 0 4 40h-12zM315 195h10l4 55h-18zM307 315h26l7 82h-40zM294 470h52l8 90h-68z" fill="#d8e2c6" opacity=".72"/>
                    <path d="M107 492 218 75M533 492 422 75" stroke="#89988d" stroke-opacity=".23" stroke-width="2"/>
                    <ellipse cx="371" cy="359" rx="68" ry="31" fill="#0a1110" opacity=".48" filter="url(#soft-shadow)"/>
                    <path d="M326 347c11-18 25-27 42-24 13 3 19 13 34 14 14 1 25 10 26 21 2 14-13 25-31 25-16 0-23 13-41 11-17-2-29-12-34-24-4-9-2-16 4-23z" fill="#111715" stroke="#7f8e71" stroke-width="2"/>
                    <path d="M303 296h147v128H303z" fill="none" stroke="#dfff78" stroke-width="3"/>
                    <path d="M303 316v-20h20M430 296h20v20M303 404v20h20M430 424h20v-20" fill="none" stroke="#dfff78" stroke-linecap="round" stroke-width="5"/>
                    <circle cx="376" cy="359" r="95" fill="url(#road-glow)" opacity=".42"/>
                    <circle cx="376" cy="359" r="3" fill="#dfff78"/>
                    <path d="M74 101h86M74 111h46" stroke="#dfff78" stroke-opacity=".32" stroke-linecap="round" stroke-width="2"/>
                    <circle cx="515" cy="95" r="43" fill="none" stroke="#dfff78" stroke-opacity=".14"/>
                    <circle cx="515" cy="95" r="31" fill="none" stroke="#dfff78" stroke-opacity=".25"/>
                    <path d="M515 74v42M494 95h42" stroke="#dfff78" stroke-opacity=".3" stroke-width="1.5"/>
                </svg>
                <div class="landing-visual-caption">
                    <span>Road image analysis</span>
                    <span>YOLO · Vision model</span>
                </div>
            </div>
        </section>
    </div>
    """, unsafe_allow_html=True)

    if st.button("Start a report", type="primary", key="enter_platform"):
        st.session_state["show_landing"] = False
        st.rerun()

    st.markdown("""
        <section class="landing-content-section">
            <h2 class="landing-section-heading">From a road image to a repair-ready report.</h2>
            <p class="landing-section-copy">A practical workflow connects visual evidence with location details, so the right people can review an issue and act on it.</p>
            <div class="landing-process-grid">
                <article class="landing-process-card">
                    <span class="landing-process-number">01</span>
                    <h3>Capture the road</h3>
                    <p>Upload a photo or video of the damaged area. Add the location and contact details needed to follow up.</p>
                </article>
                <article class="landing-process-card">
                    <span class="landing-process-number">02</span>
                    <h3>Detect with deep learning</h3>
                    <p>A trained YOLO vision model analyzes images and sampled video frames, then marks detected potholes on the evidence.</p>
                </article>
                <article class="landing-process-card">
                    <span class="landing-process-number">03</span>
                    <h3>Route the response</h3>
                    <p>Location-aware reports can be reviewed, checked for nearby duplicates, and tracked through the maintenance workflow.</p>
                </article>
            </div>
        </section>
    """, unsafe_allow_html=True)
    st.markdown("""
        <section class="landing-content-section">
            <h2 class="landing-section-heading">AI that shows its work.</h2>
            <div class="landing-capability-panel">
                <div>
                    <h3>Deep learning for detection. Human-readable evidence for decisions.</h3>
                    <p>The detection engine uses a trained YOLO model to identify potholes in uploaded media. Severity and estimated depth are separate visual estimates derived from the detected box geometry; they are not direct depth measurements or YOLO outputs.</p>
                </div>
                <div class="landing-capability-list">
                    <div class="landing-capability-item"><b>01</b> Detect potholes in photos</div>
                    <div class="landing-capability-item"><b>02</b> Check detections across video frames</div>
                    <div class="landing-capability-item"><b>03</b> Review annotated evidence and risk estimates</div>
                </div>
            </div>
        </section>
    """, unsafe_allow_html=True)
    st.markdown("""
        <section class="landing-content-section">
            <h2 class="landing-section-heading">Built for reporting and response.</h2>
            <p class="landing-section-copy">Citizens can submit evidence and follow a complaint. Municipal teams get tools to review reports and coordinate the next step.</p>
            <div class="landing-portal-grid">
                <article class="landing-portal-card">
                    <span class="landing-portal-label">Public reporting</span>
                    <h3>For the people on the road</h3>
                    <p>Submit a pothole photo or video, share location details, and keep the tracking ID to check progress later.</p>
                </article>
                <article class="landing-portal-card">
                    <span class="landing-portal-label">Operations workspace</span>
                    <h3>For the teams fixing it</h3>
                    <p>Review reports, inspect detections on a map, prioritize follow-up, and manage contractor work orders.</p>
                </article>
            </div>
        </section>
        <footer class="landing-footer">
            <strong>Pothole Detection</strong>
            <span>Pothole intelligence · Location-aware reporting</span>
        </footer>
    """, unsafe_allow_html=True)


if st.session_state["user_role"] is None and st.session_state["show_landing"]:
    render_landing_page()
    st.stop()


# --- Login Screen ---
def render_login_screen():
    if notice := st.session_state.pop("auth_session_notice", None):
        st.warning(notice)
    if st.button("← Back to introduction", key="login_back_button"):
        st.session_state["show_landing"] = True
        st.rerun()

    st.markdown("""
    <section class="portal-intro">
        <div class="portal-intro-kicker">POTHOLE DETECTION · YOLO OPERATIONS</div>
        <h1>Choose how you want to make a difference.</h1>
        <p>Report a road hazard as a citizen, or sign in as a municipal authority to review and coordinate repairs.</p>
    </section>
    """, unsafe_allow_html=True)

    with st.container(key="portal_screen"):
        col1, col2 = st.columns(2, gap="large")

        with col1:
            with st.container(border=True, key="citizen_portal_card"):
                st.markdown("""
                <div class="portal-card-heading">
                    <span class="portal-card-icon citizen" role="img" aria-label="Citizen and community">
                        <svg viewBox="0 0 32 32" aria-hidden="true">
                            <circle cx="16" cy="9" r="4.2" fill="currentColor" stroke="none"/>
                            <path d="M8.5 26c.5-5.3 3.2-8.3 7.5-8.3s7 3 7.5 8.3"/>
                            <circle cx="6.8" cy="13" r="2.6" fill="none"/>
                            <circle cx="25.2" cy="13" r="2.6" fill="none"/>
                            <path d="M2.8 25c.4-3.3 1.7-5.3 4-5.3 1.5 0 2.7.7 3.5 2"/>
                            <path d="M29.2 25c-.4-3.3-1.7-5.3-4-5.3-1.5 0-2.7.7-3.5 2"/>
                        </svg>
                    </span>
                    <div>
                        <div class="portal-card-eyebrow">PUBLIC REPORTING</div>
                        <h2>Citizen portal</h2>
                    </div>
                </div>
                <p class="portal-card-copy">Capture a pothole with a photo or video, share its location, and follow your report with a tracking ID.</p>
                """, unsafe_allow_html=True)
                if st.button("Continue as citizen", type="primary", use_container_width=True, key="citizen_continue"):
                    st.session_state["user_role"] = "citizen"
                    persist_workspace_session("citizen")
                    st.rerun()

        with col2:
            with st.container(border=True, key="authority_portal_card"):
                st.markdown("""
                <div class="portal-card-heading">
                    <span class="portal-card-icon authority" role="img" aria-label="Municipal government">
                        <svg viewBox="0 0 32 32" aria-hidden="true">
                            <path d="M4 13.5 16 6l12 7.5"/>
                            <path d="M6.5 14h19M7.5 26h17M5 28h22"/>
                            <path d="M9 15v9M14 15v9M18 15v9M23 15v9"/>
                            <circle cx="16" cy="8" r="1.7" fill="currentColor" stroke="none"/>
                        </svg>
                    </span>
                    <div>
                        <div class="portal-card-eyebrow">OPERATIONS WORKSPACE</div>
                        <h2>Municipal authority</h2>
                    </div>
                </div>
                <p class="portal-card-copy">Sign in to review AI-assisted detections, inspect reports on a map, and coordinate maintenance work.</p>
                """, unsafe_allow_html=True)
                with st.form("authority_login_form"):
                    identifier = st.text_input(
                        "Work email",
                        placeholder="you@organization.gov",
                        autocomplete="email",
                    )
                    submitted = st.form_submit_button("Send secure sign-in code", use_container_width=True)
                    if submitted:
                        response = api_request("POST", "/api/auth/login", json={"role": "authority", "identifier": identifier})
                        if response is not None and response.status_code == 200:
                            login_result = response.json()
                            if login_result.get("otp_required"):
                                st.session_state["otp_challenge_id"] = login_result["challenge_id"]
                                st.session_state["otp_email"] = login_result["email"]
                                st.session_state["otp_expires_at"] = login_result["expires_at"]
                                if login_result.get("already_sent"):
                                    st.info(f"The existing OTP sent to {login_result['email']} is still valid. Use that code.")
                                else:
                                    st.info(f"A 6-digit OTP was sent to {login_result['email']}.")
                            else:
                                st.session_state["user_role"] = "authority"
                                st.session_state["staff_session"] = login_result
                                persist_workspace_session("authority", login_result)
                                st.rerun()
                        elif response is not None:
                            st.error(response.json().get("detail", "Invalid authority credentials."))

                if st.session_state.get("otp_challenge_id"):
                    components.html(
                        f"""
                        <div id="otp-countdown" style="font: 600 16px sans-serif; color: #65704f; margin: 8px 0 12px;">
                            OTP expires in 30:00
                        </div>
                        <script>
                            const target = new Date({st.session_state["otp_expires_at"]!r}).getTime();
                            const display = document.getElementById("otp-countdown");
                            const updateCountdown = () => {{
                                const remaining = Math.max(0, target - Date.now());
                                const minutes = Math.floor(remaining / 60000);
                                const seconds = Math.floor((remaining % 60000) / 1000);
                                display.textContent = remaining > 0
                                    ? `OTP expires in ${{minutes}}:${{String(seconds).padStart(2, "0")}}`
                                    : "OTP expired. Request a new code.";
                            }};
                            updateCountdown();
                            setInterval(updateCountdown, 1000);
                        </script>
                        """,
                        height=42,
                    )
                    with st.form("authority_otp_form"):
                        st.caption(f"Enter the OTP sent to {st.session_state['otp_email']}")
                        otp = st.text_input("One-time password", max_chars=6, placeholder="123456")
                        if st.form_submit_button("Verify one-time code", type="primary", use_container_width=True):
                            response = api_request(
                                "POST", "/api/auth/verify-otp",
                                json={"challenge_id": st.session_state["otp_challenge_id"], "otp": otp},
                            )
                            if response is not None and response.status_code == 200:
                                st.session_state["user_role"] = "authority"
                                st.session_state["staff_session"] = response.json()
                                persist_workspace_session("authority", response.json())
                                st.session_state.pop("otp_challenge_id", None)
                                st.session_state.pop("otp_email", None)
                                st.session_state.pop("otp_expires_at", None)
                                st.rerun()
                            elif response is not None:
                                st.error(response.json().get("detail", "Invalid or expired OTP."))


if st.session_state["user_role"] is None:
    render_login_screen()
    st.stop()


# --- Main Application Sidebar ---
defects_list = fetch_defects()
staff_session = st.session_state.get("staff_session")
authority_complaints_list = fetch_authority_complaints(
    staff_session.get("access_token") if staff_session else None
)

with st.sidebar:
    st.markdown("## 🛰️ Pothole Detection")
    role_label = "Citizen Workspace" if st.session_state["user_role"] == "citizen" else "Authority Workspace"
    st.caption("Pothole intelligence platform")
    st.caption(role_label)
    st.divider()
    
    if st.session_state["user_role"] == "citizen":
        pages = ["New Report", "Track Complaint"]
    else:
        pages = ["Dashboard", "Reports", "Map View", "Work Orders", "Analytics"]

    requested_page = st.query_params.get("page", pages[0])
    initial_page = requested_page if requested_page in pages else pages[0]
    page = st.radio(
        "Navigation",
        pages,
        index=pages.index(initial_page),
        key="workspace_page",
        label_visibility="collapsed",
    )
    if st.query_params.get("page") != page:
        st.query_params["page"] = page
    st.divider()
    
    if st.session_state["user_role"] == "authority":
        st.success("✓ Verified Authority")
        
    if backend_is_available():
        st.info("🟢 API Connected")
    else:
        st.error("🔴 API Offline")
    
    if st.button("Sign Out", use_container_width=True):
        st.session_state.pop("staff_session", None)
        st.session_state["user_role"] = None
        st.session_state["show_landing"] = False
        clear_workspace_session()
        st.query_params.clear()
        st.rerun()


# --- Workspace Router ---
if page == "New Report":
    st.markdown("<div class='animated-element'>", unsafe_allow_html=True)
    render_workspace_hero(
        "CITIZEN INTAKE · LIVE ANALYSIS",
        "Report infrastructure damage",
        "Turn a road photo or video into a location-aware, review-ready maintenance report.",
    )
    
    report_column, map_column = st.columns([1.1, 0.9], gap="large")

    with report_column:
        with st.container(border=True):
            st.subheader("📸 1. Upload Evidence")
            uploaded_media = st.file_uploader("Select a clear photo or short MP4 video of the defect.", type=MEDIA_TYPES)
            if uploaded_media is not None:
                render_preview(uploaded_media)

        with st.container(border=True):
            st.subheader("📍 2. Location & Contact Details")
            st.write("Grant GPS access for precise tagging, or type the address below.")
            
            location = streamlit_geolocation()
            latitude = location.get("latitude") if location else None
            longitude = location.get("longitude") if location else None

            active_lat, active_lon = (
                latitude if latitude is not None else DEFAULT_LOCATION_LATITUDE,
                longitude if longitude is not None else DEFAULT_LOCATION_LONGITUDE,
            )

            if latitude is not None and longitude is not None:
                st.success(f"GPS Locked: {latitude:.6f}, {longitude:.6f}")
                manual_address = st.text_area("Detailed Address / Landmark (Optional)", height=70)
            else:
                manual_address = st.text_area(
                    "Full Street Address",
                    value=DEFAULT_LOCATION_ADDRESS,
                    height=100,
                )
                if manual_address.strip() and manual_address.strip() != DEFAULT_LOCATION_ADDRESS:
                    geo_lat, geo_lon = geocode_manual_address(manual_address)
                    if geo_lat and geo_lon:
                        active_lat, active_lon = geo_lat, geo_lon
            
            pincode = st.text_input(
                "Enter Area Pincode / Postcode",
                value=DEFAULT_LOCATION_PINCODE,
                max_chars=8,
                placeholder="e.g. 522213 or SW1A 1AA",
                help="Used to route to the correct municipal ward.",
            )
            reporter_phone = st.text_input("Enter your phone number", placeholder="e.g. +91 9876543210")
            reporter_email = st.text_input("Enter your email address", placeholder="you@example.com")
            severity = st.selectbox("Select Severity", ["High", "Medium", "Low"])
            
            if pincode.strip() and len(pincode.strip()) <= 8:
                jurisdiction = api_request("GET", f"/api/pincodes/{pincode.strip()}")
                if jurisdiction is not None and jurisdiction.status_code == 200:
                    authority = jurisdiction.json()
                    routing_details = [authority.get("authority_name", "Municipal authority")]
                    if authority.get("department"):
                        routing_details.append(authority["department"])
                    if authority.get("ward_number"):
                        routing_details.append(f"Ward {authority['ward_number']}")
                    st.success(f"🏛️ Routing to: {' | '.join(routing_details)}")
                elif jurisdiction is not None and jurisdiction.status_code == 404:
                    st.warning("No active authority mapped to this pincode yet.")

        if st.button("🚀 Analyze & Submit Report", type="primary", use_container_width=True):
            if uploaded_media is None:
                st.error("Please upload a photo or video first.")
            elif active_lat is None and not manual_address.strip():
                st.error("Please provide an address or grant GPS permissions.")
            else:
                with st.spinner("🤖 AI is analyzing the media and evaluating pothole severity..."):
                    try:
                        if not pincode.strip() or len(pincode.strip()) > 8:
                            st.error("A valid pincode or postcode is required.")
                            response = None
                        elif not reporter_phone.strip():
                            st.error("A phone number is required to track the status.")
                            response = None
                        elif "@" not in reporter_email or "." not in reporter_email.rsplit("@", 1)[-1]:
                            st.error("A valid email address is required.")
                            response = None
                        else:
                            response = analyze_uploaded_media(uploaded_media, active_lat, active_lon, manual_address, pincode, severity, reporter_phone, reporter_email)
                        
                        if response is not None and response.status_code == 200:
                            analysis_result = response.json()
                            st.session_state["analysis"] = analysis_result
                            complaint = analysis_result.get("complaint", {})
                            if complaint.get("id") is not None:
                                st.session_state["last_complaint_id"] = complaint["id"]
                                st.session_state["last_reporter_phone"] = reporter_phone.strip()
                            requests.get(f"{BACKEND_BASE_URL}/api/geo/map", timeout=5)
                            st.rerun()
                        elif response is not None:
                            st.error(response.json().get("detail", "The backend could not analyze this media."))
                    except requests.RequestException as error:
                        st.error(f"Backend unavailable: {error}")

        # Post-analysis Display
        analysis = st.session_state.get("analysis")
        if analysis:
            st.divider()
            if analysis.get("status") == "NO_DEFECT_DETECTED":
                st.info("ℹ️ " + analysis.get("message", "No defect was confirmed."))
            elif analysis.get("status") == "ALREADY_REGISTERED":
                complaint = analysis.get("complaint", {})
                st.warning(f"This complaint is already registered. Track ID: {complaint.get('id', 'Unavailable')}")
            else:
                vision = analysis.get("vision", {})
                st.success(f"✅ AI Analysis Complete: {vision.get('defect_type', 'Road Defect')}")
                annotated_image = requests.get(f"{BACKEND_BASE_URL}/api/analysis/annotated-image", timeout=10)
                if annotated_image.status_code == 200:
                    st.image(annotated_image.content, caption="AI pothole detection bounding box", use_container_width=True)
                st.write(f"**Address:** {analysis.get('address')}")
                st.write(f"**Road Risk Profile:** {'⚠️ HIGH RISK' if analysis.get('terrain_exposure') else '🟢 Normal'}")
                
                ecol1, ecol2 = st.columns(2)
                ecol1.metric("Calculated Severity", vision.get("severity_level") or "Unavailable")
                depth = vision.get("estimated_depth_cm")
                ecol2.metric("Estimated Depth", f"~{depth} cm" if depth is not None else "Unavailable")
                
                complaint = analysis.get("complaint", {})
                if complaint.get("id") is not None:
                    st.success(f"🎫 **Complaint successfully registered!** Your Tracking ID is: **#{complaint['id']}**")
                    components.html(
                        f"""<div style='display:flex;align-items:center;gap:8px;font-family:sans-serif;color:#f8fafc'>
                        <strong style='font-size:13px;color:#f8fafc'>Tracking ID</strong>
                        <code id='tracking-id' style='font-size:13px;color:#f8fafc;background:transparent'>{complaint['id']}</code>
                        <button onclick=\"navigator.clipboard.writeText(document.getElementById('tracking-id').innerText)\" title='Copy tracking ID' style='border:1px solid #94a3b8;background:#f8fafc;color:#0f172a;border-radius:4px;cursor:pointer;font-size:16px;line-height:1;padding:4px 7px'>📋</button>
                        </div>""",
                        height=35,
                    )
                email = analysis.get("email", {})
                if email.get("gmail_url"):
                    st.link_button("📧 Send mail to Pothole Detection Authority", email["gmail_url"], use_container_width=True)

    with map_column:
        st.subheader("🗺️ Live Dispatch Map")
        render_dynamic_map(lat=active_lat, lon=active_lon, label=manual_address or "Selected Location")
        st.markdown("</div>", unsafe_allow_html=True)


elif page == "Track Complaint":
    st.markdown("<div class='animated-element'>", unsafe_allow_html=True)
    render_workspace_hero(
        "CITIZEN SIGNAL · STATUS",
        "Track your complaint",
        "Follow your report from first signal to field action with your tracking ID and phone number.",
    )
    
    with st.container(border=True):
        id_column, phone_column = st.columns([1, 1])
        complaint_id = id_column.text_input("Tracking ID", value=st.session_state.get("last_complaint_id", ""), placeholder="CMP-2026-00002")
        reporter_phone = phone_column.text_input("Phone Number", value=st.session_state.get("last_reporter_phone", ""), placeholder="+91 9876543210")
        
        if st.button("🔍 Check Status", type="primary"):
            response = api_request("GET", f"/api/complaints/{quote(complaint_id.strip())}", params={"reporter_phone": reporter_phone})
            if response is not None and response.status_code == 200:
                complaint = response.json()
                status_labels = {
                    "PENDING_VERIFICATION": ("REPORTED", "#dc2626"),
                    "IN_PROGRESS": ("WORKING", "#ca8a04"),
                    "ASSIGNED_TO_CONTRACTOR": ("WORKING", "#ca8a04"),
                    "RESOLVED": ("DONE", "#16a34a"),
                }
                label, color = status_labels.get(complaint.get("status"), (complaint.get("status", "UNKNOWN"), "#6b7280"))
                st.markdown(f"<div style='background:{color};color:white;padding:0.75rem 1rem;border-radius:0.5rem;font-weight:700;text-align:center'>STATUS: {label}</div>", unsafe_allow_html=True)
                
                c1, c2, c3 = st.columns(3)
                c1.metric("Severity", complaint["severity_level"])
                c2.metric("Est. Depth", f"~{complaint['estimated_depth_cm']} cm" if complaint["estimated_depth_cm"] is not None else "N/A")
                c3.metric("Location", complaint["address"] or "Unavailable")
            elif response is not None:
                st.error(response.json().get("detail", "Ticket not found or phone number mismatch."))
    st.markdown("</div>", unsafe_allow_html=True)


elif page == "Dashboard":
    render_workspace_hero(
        "OPERATIONS CENTER · AUTHORITY",
        "Authority dashboard",
        "See active infrastructure risk, review incoming complaints, and move verified work into delivery.",
    )
    if notice := st.session_state.pop("dashboard_notice", None):
        st.success(notice)
    
    all_dashboard_records = dashboard_records_for_session(
        authority_complaints_list, defects_list, staff_session
    )
    dashboard_records = (
        [record for record in all_dashboard_records if is_active_complaint(record)]
        if staff_session
        else all_dashboard_records
    )
    total = len(dashboard_records)
    critical = sum(
        str(row.get("severity_level", row.get("severity", ""))).lower() in {"high", "critical"}
        for row in dashboard_records
    )
    medium = sum(
        str(row.get("severity_level", row.get("severity", ""))).lower() == "medium"
        for row in dashboard_records
    )
    pothole_risk = sum(row.get("terrain_exposure") in [1, True, "True"] for row in dashboard_records)
    
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Reports", total)
    c2.metric("🔴 Critical Priority", critical)
    c3.metric("🟡 Medium Priority", medium)
    c4.metric("🕳️ Pothole Hazards", pothole_risk)
    
    st.markdown("<br/>", unsafe_allow_html=True)
    render_dynamic_map(height=500)
    
    staff_session = st.session_state.get("staff_session")
    if staff_session:
        st.divider()
        st.subheader("Action Required: Review Queue")
        headers = {"Authorization": f"Bearer {staff_session['access_token']}"}
        headers = {"Authorization": "Bearer " + staff_session["access_token"]}
        response = api_request("GET", "/api/authority/complaints", headers=headers)
        if response is not None and response.status_code == 200:
            complaints = [
                item for item in response.json().get("complaints", [])
                if is_active_complaint(item)
            ]
            if complaints:
                st.dataframe(pd.DataFrame(complaints), use_container_width=True)
            else:
                st.info("✅ All caught up! No complaints waiting for review.")
            complaint_ids = [
                str(item.get("complaint_id") or item.get("id"))
                for item in complaints
                if item.get("complaint_id") or item.get("id")
            ]
            with st.container(border=True):
                st.write("**Update Complaint Status**")
                col_a, col_b = st.columns(2)
                selected_id = col_a.selectbox(
                    "Select Complaint",
                    complaint_ids or ["No complaints available"],
                    disabled=not complaint_ids,
                )
                selected_status = col_b.selectbox(
                    "Set New Status",
                    ["PENDING_VERIFICATION", "IN_PROGRESS", "RESOLVED"],
                )
                if st.button("Update System", type="primary", disabled=not complaint_ids):
                    update = api_request(
                        "PATCH",
                        f"/api/authority/complaints/{quote(selected_id)}",
                        headers=headers,
                        json={"status": selected_status},
                    )
                    if update is not None and update.status_code == 200:
                        updated = update.json()
                        st.cache_data.clear()
                        st.session_state["dashboard_notice"] = (
                            f"Ticket #{selected_id} updated to "
                            f"{updated.get('status', selected_status)}."
                        )
                        st.rerun()
                    elif update is not None:
                        st.error(response_detail(update, "Update failed."))
                    else:
                        st.error("Could not reach the service to update this complaint.")
        elif response is not None:
            if response.status_code == 401:
                st.session_state.pop("staff_session", None)
                st.session_state["user_role"] = None
                st.session_state["show_landing"] = False
                clear_workspace_session()
                st.query_params.clear()
                st.session_state["auth_session_notice"] = (
                    "Your authority session expired. Please sign in again to load the review queue."
                )
                st.rerun()
            st.error(response_detail(response, "Could not load the review queue."))
        else:
            st.error("Could not reach the service to load the review queue.")


elif page == "Reports":
    render_workspace_hero(
        "EVIDENCE LEDGER · AUTHORITY",
        "Complaint ledger",
        "A complete, searchable view of every complaint routed to your authority workspace.",
    )
    if authority_complaints_list:
        st.dataframe(pd.DataFrame(authority_complaints_list), use_container_width=True, height=320)
    else:
        st.info("No recorded reports yet.")

elif page == "Map View":
    col1, col2 = st.columns([0.8, 0.2])
    with col1:
        render_workspace_hero(
            "SPATIAL INTELLIGENCE · GIS",
            "Global city map",
            "See where road risk is clustering and refresh the live dispatch layer.",
        )
    if col2.button("🔄 Refresh Map Data", use_container_width=True):
        try:
            requests.get(f"{BACKEND_BASE_URL}/api/geo/map", timeout=5)
            st.rerun()
        except requests.RequestException:
            st.warning("The backend is unavailable.")
    render_dynamic_map(height=650)

elif page == "Work Orders":
    render_workspace_hero(
        "FIELD DELIVERY · PRIORITY QUEUE",
        "Active work orders",
        "Monitor the repair queue and the latest status of work moving through the city.",
    )
    if authority_complaints_list:
        report_frame = pd.DataFrame(authority_complaints_list)
        visible_columns = [col for col in ["complaint_id", "complaint_type", "severity_level", "status", "updated_at", "manual_address"] if col in report_frame.columns]
        st.dataframe(report_frame[visible_columns], use_container_width=True)
    else:
        st.info("No work orders have been dispatched yet.")

elif page == "Analytics":
    render_workspace_hero(
        "DECISION SUPPORT · INSIGHTS",
        "Intelligence analytics",
        "Translate complaint volume and severity into a clearer operating picture.",
    )
    if authority_complaints_list:
        report_frame = pd.DataFrame(authority_complaints_list)
        category_column, severity_column = st.columns(2)
        with category_column:
            st.subheader("Defect Distribution")
            if "complaint_type" in report_frame:
                st.bar_chart(report_frame["complaint_type"].value_counts())
        with severity_column:
            st.subheader("Severity Breakdown")
            if "severity_level" in report_frame:
                st.bar_chart(report_frame["severity_level"].value_counts())
    else:
        st.info("Analytics require recorded reports to generate graphs.")

elif page == "Settings":
    render_workspace_hero(
        "CONTROL ROOM · CONFIGURATION",
        "System preferences",
        "Review the connected service endpoint and workspace configuration.",
    )
    with st.container(border=True):
        st.text_input("FastAPI Base URL Endpoint", value=BACKEND_BASE_URL)