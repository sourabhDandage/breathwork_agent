# LinkedIn post draft

## Suggested headline

What if your next breathing practice started with a signal from your body?

## Post copy

Anxiety and stress often arrive before we have words for them.

I built **Prana Pulse**, a small breathwork app that connects Garmin heart-rate data with traditional pranayama guidance.

Every hour, it creates a gentle awareness check-in that can:

- Read the latest heart-rate samples from Garmin Connect
- Translate that signal into a gentle breathing recommendation
- Suggest a calming, balancing, or energizing practice
- Keep the experience simple enough to use between meetings, classes, or commutes
- Guide one short practice capped at 90 seconds

The goal is not to diagnose stress or replace professional care. It is to create a small pause: notice the signal, soften the breath, and choose a practice intentionally. The 90-second cap keeps the interaction light and approachable.

The current prototype uses:

- `python-garminconnect` for Garmin Connect data
- A lightweight local Python webapp
- Hourly heart-rate refreshes
- A simple rules-based recommendation layer
- Local token storage and no unnecessary data collection

For example:

- A higher reading can suggest **Nadi Shodhana**, a balancing practice
- A steady reading can suggest **Bhramari**, a settling humming practice
- A lower resting reading can suggest an energizing practice, with a reminder to stop if you feel dizzy or unwell

The dashboard now also visualizes each practice as a breathing rhythm. For
example, Box Breathing displays four equal phases: inhale, hold, exhale, hold.
The visualizer includes a 90-second maximum session timer, plus pause and
restart controls, so the experience stays a gentle invitation rather than a
test of endurance.

This is an early, practical experiment in making wellbeing support more timely and personal.

I am especially interested in the intersection of wearable signals, traditional breathwork, and humane technology: tools that help us pay attention without demanding more attention from us.

What would you want a stress-aware breathing app to notice before suggesting a practice?

#Breathwork #Pranayama #StressManagement #AnxietySupport #WearableTechnology #Python #Wellbeing #DigitalHealth

## Image carousel

### Slide 1: The project

**Image:** A clean screenshot of the Prana Pulse dashboard showing the heart-rate panel and “Next practice” section.

**Overlay text:**

> PRANA/PULSE
> Breathe with your body's signal.

**Alt text:** Prana Pulse dashboard for hourly heart-rate-based breathwork guidance.

### Slide 2: The loop

**Image:** A simple three-step visual using the project's sage, coral, and green palette.

**Overlay text:**

> Notice -> Interpret -> Breathe
>
> Garmin signal -> Gentle guidance -> One-minute pause

**Alt text:** Three-step flow from wearable heart-rate data to a pranayama suggestion.

### Slide 3: The recommendation

**Image:** A close crop of the recommendation panel with a subtle breath-wave line.

**Overlay text:**

> A signal is not a diagnosis.
> It is an invitation to check in.

**Alt text:** Breathwork recommendation presented as supportive guidance rather than medical advice.

### Slide 4: The guardrail

**Image:** Minimal text-led slide with a calm off-white background and small footer mark.

**Overlay text:**

> Built for a pause,
> not a prescription.
>
> Stop if you feel unwell.
> Seek professional support when needed.

**Alt text:** Safety statement clarifying that the app does not diagnose or replace professional care.

## Image production notes

- Use a real screenshot of the local dashboard for Slide 1.
- Blur or crop any email addresses, tokens, timestamps, or personal health details.
- Keep text large and readable on mobile.
- Export carousel images at 1080 x 1350 px for LinkedIn portrait posts.
- Use the app's existing colors: warm off-white, sage green, deep green, and coral.
- Avoid before/after claims, guaranteed outcomes, or language implying medical diagnosis.

## Short version

I built **Prana Pulse**, a prototype that uses Garmin heart-rate data to suggest a gentle pranayama practice every hour.

It is designed for a simple moment of awareness when stress or anxiety starts to build: notice the signal, soften the breath, and choose a pause.

Not a diagnosis. Not a replacement for professional care. Just a small experiment in making breathwork more timely and personal.

#Breathwork #Pranayama #WearableTechnology #StressManagement #Python
