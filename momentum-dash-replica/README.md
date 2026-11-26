# New Tab Dashboard

## Purpose

This Chrome extension replaces the new-tab page with a clock, original daily note,
reminders, a to-do list, a personal goal tracker, and customizable backgrounds.

## Data collection

Original daily notes created for this project are loaded from the bundled
[`quotes.json`](./quotes.json). The extension does not fetch news or contact an
external service.

## Data persistence

Reminders, tasks, goal progress, selected background, and uploaded background
image are stored in Chrome local storage within the browser profile. This
information is not sent to an application backend or synchronized across
devices.

## User interaction

After installation, opening a new tab displays the time, a daily note, and three
widgets. Add reminders with a date and time, add and complete to-do items, and
set one personal goal with manually updated progress. Due reminders are
highlighted when the new-tab page is open; the extension does not send system
notifications. Open the settings button to choose a background preset, upload
an image, or restore the default.

## Setup

To install the extension locally:

1. Open `chrome://extensions` in Chrome.
2. Turn on **Developer mode**.
3. Select **Load unpacked** and choose this project directory.
4. Open a new tab.

The extension uses Chrome's `storage` API and has no npm dependencies or
build step. Load this directory unpacked from `chrome://extensions`. Run its
tests with `npm test` using Node.js 20 or later.

## Learning

The project practices Chrome's new-tab override, browser local storage,
accessible forms, DOM updates, image resizing, and client-side state
management. A key challenge is keeping widget state persistent while keeping
the interface responsive and usable on different screen sizes.

## Limitations and assistance

Widget data is local to the browser profile and is not synchronized. Due
reminders are shown only while the new-tab page is open; they do not trigger
system notifications. Uploaded images consume browser storage.

The extension uses Chrome APIs and has no runtime network dependency. No
externally copied source-code snippets are identified in this project. The
repository's MIT license covers original project code only; see
[the third-party notices](../THIRD_PARTY_NOTICES.md) for content exclusions.
