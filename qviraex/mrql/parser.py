from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Any

from .ast import Block, FieldBlock, MetadataBlock, OperationBlock, RitualDocument, SequenceBlock


class MRQLParseError(ValueError):
    pass


@dataclass(frozen=True)
class _Line:
    number: int
    text: str


class MRQLParser:
    _ritual_header = re.compile(r"^ritual\s+(?P<name>[A-Za-z_][\w-]*)\s+v(?P<version>[0-9]+(?:\.[0-9]+)*)\s*\{$")
    _section_header = re.compile(r"^(?P<section>metadata|constraints|field|sequence)(?:\s+(?P<name>[A-Za-z_][\w-]*))?\s*\{$")
    _operation_header = re.compile(r"^(?P<operation>[A-Z_]+)\s*\{$")
    _key_value = re.compile(r"^(?P<key>[A-Za-z_][\w\.]*)\s*:\s*(?P<value>.+)$")
    _comparison = re.compile(r"^(?P<key>[A-Za-z_][\w\.]*)\s*(?P<op>==|!=|<=|>=|<|>)\s*(?P<value>.+)$")

    def parse(self, source: str) -> RitualDocument:
        lines = self._prepare_lines(source)
        if not lines:
            raise MRQLParseError("empty MRQL source")

        header = self._match(self._ritual_header, lines[0])
        if header is None:
            raise MRQLParseError(f"line {lines[0].number}: expected ritual header")

        blocks, closing_line = self._parse_document_body(lines[1:])
        if closing_line is None:
            raise MRQLParseError("missing closing brace for ritual")

        return RitualDocument(
            name=header["name"],
            version=header["version"],
            metadata=blocks.get("metadata"),
            constraints=blocks.get("constraints"),
            field=blocks.get("field"),
            sequence=blocks.get("sequence"),
            raw_text=source,
        )

    def _parse_document_body(self, lines: list[_Line]) -> tuple[dict[str, Block], int | None]:
        blocks: dict[str, Block] = {}
        index = 0
        while index < len(lines):
            line = lines[index]
            if line.text == "}":
                return blocks, line.number

            section = self._match(self._section_header, line)
            if section is None:
                raise MRQLParseError(f"line {line.number}: expected section header")

            section_lines, next_index = self._collect_block(lines, index)
            name = section["section"]
            if name == "metadata":
                blocks[name] = MetadataBlock(name="metadata", values=self._parse_key_value_block(section_lines[1:-1]))
            elif name == "constraints":
                blocks[name] = Block(name="constraints", values=self._parse_constraints(section_lines[1:-1]))
            elif name == "field":
                blocks[name] = FieldBlock(name=section["name"] or "field", values=self._parse_key_value_block(section_lines[1:-1]))
            elif name == "sequence":
                blocks[name] = SequenceBlock(name="sequence", operations=self._parse_operations(section_lines[1:-1]))
            else:
                raise MRQLParseError(f"line {line.number}: unsupported section {name}")
            index = next_index

        return blocks, None

    def _collect_block(self, lines: list[_Line], start_index: int) -> tuple[list[_Line], int]:
        depth = 0
        collected: list[_Line] = []
        index = start_index
        while index < len(lines):
            line = lines[index]
            collected.append(line)
            depth += line.text.count("{")
            depth -= line.text.count("}")
            if depth == 0:
                return collected, index + 1
            index += 1
        raise MRQLParseError(f"line {lines[start_index].number}: unterminated block")

    def _parse_key_value_block(self, lines: list[_Line]) -> dict[str, Any]:
        values: dict[str, Any] = {}
        for line in lines:
            match = self._match(self._key_value, line)
            if match is None:
                raise MRQLParseError(f"line {line.number}: expected key/value pair")
            values[match["key"]] = self._coerce_value(match["value"])
        return values

    def _parse_constraints(self, lines: list[_Line]) -> dict[str, Any]:
        constraints: dict[str, Any] = {}
        for line in lines:
            match = self._match(self._comparison, line)
            if match is None:
                raise MRQLParseError(f"line {line.number}: expected constraint expression")
            constraints[match["key"]] = {"op": match["op"], "value": self._coerce_value(match["value"])}
        return constraints

    def _parse_operations(self, lines: list[_Line]) -> tuple[OperationBlock, ...]:
        operations: list[OperationBlock] = []
        index = 0
        while index < len(lines):
            line = lines[index]
            if not line.text:
                index += 1
                continue
            match = self._match(self._operation_header, line)
            if match is None:
                raise MRQLParseError(f"line {line.number}: expected operation block")
            operation_lines, next_index = self._collect_block(lines, index)
            arguments = self._parse_key_value_block(operation_lines[1:-1])
            operations.append(OperationBlock(name=match["operation"], arguments=arguments))
            index = next_index
        return tuple(operations)

    def _prepare_lines(self, source: str) -> list[_Line]:
        prepared: list[_Line] = []
        for number, raw in enumerate(source.splitlines(), start=1):
            stripped = raw.split("#", 1)[0].strip()
            if stripped:
                prepared.append(_Line(number=number, text=stripped))
        return prepared

    def _coerce_value(self, raw: str) -> Any:
        value = raw.rstrip(",")
        if value in {"true", "false"}:
            return value == "true"
        if value.startswith("[") or value.startswith("{"):
            return json.loads(value)
        if value.startswith('"') and value.endswith('"'):
            return value[1:-1]
        if value.startswith("'") and value.endswith("'"):
            return value[1:-1]
        try:
            if "." in value:
                return float(value)
            return int(value)
        except ValueError:
            return value

    def _match(self, pattern: re.Pattern[str], line: _Line) -> dict[str, str] | None:
        match = pattern.match(line.text)
        return match.groupdict() if match else None


def parse_mrql(source: str) -> RitualDocument:
    return MRQLParser().parse(source)