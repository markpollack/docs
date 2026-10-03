---
title: "JSON Mappers"
sidebarTitle: "JSON Mappers"
description: "Why acp-core has no JSON implementation, the Jackson 2 and 3 modules, and how one gets picked"
---

## `acp-core` has no databind

Since 0.18.0, `acp-core` depends on `jackson-annotations` only, not on `jackson-databind` or
`jackson-core`. The JSON implementation is a separate SPI (`AcpJsonMapper`, chosen at runtime through
`AcpJsonMapperSupplier`, a `ServiceLoader` provider), so applications that need a specific Jackson
version, or a different library entirely, aren't forced into whatever `acp-core` happened to pin.

```java
public interface AcpJsonMapper {
    static AcpJsonMapper createDefault();
    <T> T readValue(String json, TypeRef<T> type);
    <T> T convertValue(Object value, TypeRef<T> type);
    String writeValueAsString(Object value);
}
```

If you depend on `acp-core` alone with no JSON module, `AcpJsonMapper.createDefault()` fails with "No
AcpJsonMapperSupplier found on the classpath". `acp-agent-support`, `acp-test`,
`acp-streamable-http-jetty`, and the acp-autoconfig starter all already bring `acp-json-jackson2`
transitively, so most applications never need to think about this; a library consuming `acp-core`
directly does.

## Two modules, one wire format

| Module | Mapper | Priority |
|---|---|---|
| `acp-json-jackson2` | `JacksonAcpJsonMapper` (Jackson 2) | `-200` |
| `acp-json-jackson3` | `Jackson3AcpJsonMapper` (Jackson 3, 3.1.5+, the version Spring Boot 4.1 manages) | `-100` |

Both write identical bytes on the wire; the choice is purely about which Jackson major version your
application already carries. With both modules on the classpath, Jackson 3 wins (the higher
priority); an application's own `AcpJsonMapperSupplier` wins over either, and the system property
`acp.json.mapper.supplier` names one explicitly when more than one choice needs to be pinned.

```java
// Starting from a specific, pre-configured ObjectMapper instead of the module's default
var mapper = new JacksonAcpJsonMapper(myObjectMapper);
```

`JacksonAcpJsonMapper.defaultObjectMapper()` / `Jackson3AcpJsonMapper.defaultJsonMapper()` return the
module's own lenient configuration; building a `JacksonAcpJsonMapper` from a bare `new ObjectMapper()`
instead is strict about unknown fields, which can reject forward-compatible messages a newer peer
sends. Start from the module's default and customize it, rather than a bare mapper, unless strictness
is specifically what you want.

## Open values and unions still deserialize cleanly

The JSON layer is also what makes [forward compatibility](/docs/acp-java-sdk/forward-compatibility)
actually work: an unrecognized union variant reads as its `Unknown*` record rather than failing the
whole message, and an unrecognized value of an open type (`StopReason`, `ToolCallStatus`, and others)
reads as that same record type holding a string its constants don't list. Neither module treats a
response missing an optional field as an error either: `AcpSchema`'s `DefaultOnNull` marker interface
lets a response read as empty when the peer answers `"result": null` (legal JSON-RPC, and what the
Python SDK sends for a handler returning `None`) or omits the result outright.

## `TypeRef`

Generic type information Java erases at runtime, for reading or converting into a parameterized type:

```java
WordCountResult count = client.sendExtRequest(METHOD, params, new TypeRef<WordCountResult>() {});
```

Used throughout the extension-method API (see [Extension Methods](/docs/acp-java-sdk/extensions)) and
anywhere else the SDK needs a caller-supplied type that isn't just `SomeClass.class`.

## Related

<CardGroup cols={2}>
  <Card title="Forward Compatibility" icon="shield-check" href="/docs/acp-java-sdk/forward-compatibility">
    What a newer peer's message looks like once it's deserialized
  </Card>
  <Card title="Installation" icon="download" href="/docs/acp-java-sdk/reference/java#installation">
    Which modules to add, and which transports already bring one
  </Card>
</CardGroup>
