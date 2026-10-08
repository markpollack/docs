---
title: "Stable vs Unstable"
sidebarTitle: "Stability"
description: "The one convention this SDK uses for unstable API, and exactly what it currently marks"
---

One convention, used consistently across the code, the docs, and the Javadoc: **an element is
unstable if and only if it carries `@UnstableAcpApi`** (`com.agentclientprotocol.sdk.annotation`).
That annotation means the element maps to something defined only in the protocol's
`schema.unstable.json`, not the stable `schema.json`. Everything else, anything without the marker,
is a stable promise.

The marker applies to the element it's directly on: a package annotation covers its classes, a type
annotation covers its members, but it does **not** propagate to subclasses or to an interface's
implementers. Docs say "unstable (`@UnstableAcpApi`)" and nothing more; the Javadoc relies on the
annotation itself rather than restating it in prose.

## What's unstable today

| Surface | Why |
|---|---|
| **Session fork** (`session/fork`) | `ForkSessionRequest`/`Response`, `SessionCapabilities.fork`, `METHOD_SESSION_FORK`, both agents' fork handlers, both clients' `forkSession`, `supportsForkSession()`/`requireForkSession()`, `@ForkSession`, and the fork request resolver |
| **Providers** (`providers/list`, `/set`, `/disable`) | `ProvidersCapabilities`, `ProviderCurrentConfig`, `ProviderInfo`, the three request/response pairs, `AgentCapabilities.providers`, `METHOD_PROVIDERS_*`, both agents' provider handlers, both clients' `listProviders`/`setProvider`/`disableProvider`, `supportsProviders()`/`requireProviders()`, `@ListProviders`/`@SetProvider`/`@DisableProvider`, and the three provider resolvers |

Neither `session/fork` nor `providers/*` is defined in the stable schema copy
(`acp-core/src/test/resources/schema/v1/schema.json`): a test suite derives the unstable surface
from that schema and fails if a public member serving an unstable method lacks the marker, or a
stable method's member carries it, so this table can't drift from the code silently.

## Everything else is stable

Initialize; authenticate (including terminal auth and `@Authenticate`); logout; every other session
method (`new`, `load`, `list`, `close`, `delete`, `resume`, `set_mode`, `set_config_option`, both
select and boolean); prompt and cancel; `$/cancel_request`; every `session/update` variant including
`session_info_update`; file system and terminal calls; permission requests; elicitation (form, URL,
and complete); extension methods; all transports; and the rest of the annotation model.

If you're using one of these and the code or Javadoc is missing `@UnstableAcpApi`, that's a bug in
the SDK to report, not a signal to treat the API as unstable yourself.
