# 07 Replan on the road

Use during the trip, from your laptop or phone. Say what changed; Claude edits trip.json, rebuilds, and tells you to redeploy.

Examples to adapt:

```
We woke up early and are already in the car. Move today's first stop 90 minutes earlier and tell me what that does to the rest of the day.
```

```
Rebuild today around the Lady Knox Geyser at 10:15. We have tickets. Plan lunch and the rest of the afternoon, keep it under 20 minutes of walking, and update the drive.
```

```
Check my email for the Hobbiton confirmation and update the app. If the time differs from the plan, tell me before you change it.
```

```
It is raining all day. Swap the outdoor items for indoor ones that still fit the family, keep the booked tickets, and rebuild.
```

After any of these: python3 app/build.py, then redeploy site/.
