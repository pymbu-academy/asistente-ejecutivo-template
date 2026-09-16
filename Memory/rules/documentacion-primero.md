---
type: Rule
title: "La documentación de un sistema ajeno se lee entera, antes de construir"
description: "Antes de diseñar o escribir código contra una API o plataforma de terceros, se lee su documentación completa y al detalle, no la página de inicio."
tags: [asistente, herramientas, apis]
aliases: [documentacion primero, leer la documentacion, antes de integrar una api]
durable: true
status: stable
generated: { by: claude-code, at: 2026-09-16T00:00:00Z }
---

# La documentación se lee entera, antes de construir

Aplica a **cualquier integración con una API o plataforma de terceros**: pagos, CRM, email,
mensajería, lo que sea.

> **Antes de diseñar o escribir código contra un sistema ajeno: leer toda su documentación al
> detalle. No la guía de inicio. Toda.**

**Por qué:** los errores caros de una integración —un cobro que queda colgado, un límite de uso que
corta a mitad de mes, un campo que ya no existe— casi nunca aparecen probando. Aparecen leyendo: la
documentación ya los tenía contestados.

## Cómo se hace

1. **Bajar la documentación y leerla completa**, no un resumen. Muchas plataformas publican
   `llms.txt` o `llms-full.txt` con todo el contenido. Un resumen automático tuerce los detalles
   que importan.
2. **La guía y la referencia técnica (el schema, el OpenAPI) son dos fuentes distintas** y a veces
   se contradicen. Se leen las dos.
3. **Medir contra el servidor real** lo que sostiene el diseño: lo que devuelve de verdad, con qué
   formato, con qué errores.
4. **Si el proveedor publica un validador, se corre el del proveedor**, además del propio.
5. **Dejar escrito qué se leyó y qué no**, con el motivo. Lo no leído es donde se esconde el error
   siguiente.
6. **No preguntarle al proveedor algo que la documentación contesta.**
