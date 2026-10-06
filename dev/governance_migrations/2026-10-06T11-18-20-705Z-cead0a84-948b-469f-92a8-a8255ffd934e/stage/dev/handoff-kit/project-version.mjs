export function parseProjectIndexTemplateVersion(text) {
  return projectIndexTemplateVersionEvidence(text)?.version ?? null;
}

export function projectIndexTemplateVersionRow(text) {
  return projectIndexTemplateVersionEvidence(text)?.row ?? null;
}

export function materializeProjectIndexTemplateVersion(text, version) {
  if (!isStableSemver(version)) return text;
  const evidence = projectIndexTemplateVersionEvidence(text);
  if (!evidence) return text;
  return String(text).slice(0, evidence.rowStart)
    + evidence.row.replace(`| ${evidence.version} |`, `| ${version} |`)
    + String(text).slice(evidence.rowEnd);
}

function projectIndexTemplateVersionEvidence(text) {
  const value = String(text);
  const normalized = value.replace(/\r\n/g, "\n");
  const visibleLines = markdownVisibleLinesOutsideHiddenBlocks(value);
  const headings = [];
  for (const item of visibleLines) if (/^## [^\r\n]+$/u.test(item.text)) headings.push({ title: item.text.trim(), line: item.line, offset: item.normalizedStart });
  const stackHeadings = headings.filter((heading) => heading.title === "## Stack");
  if (stackHeadings.length !== 1) return null;
  const stack = stackHeadings[0];
  const nextHeading = headings.find((heading) => heading.line > stack.line);
  const stackStart = stack.offset + visibleLines.find((line) => line.line === stack.line)?.text.length + 1;
  const stackEnd = nextHeading ? nextHeading.offset : normalized.length;
  const stackLines = visibleLines.filter((line) => line.normalizedStart >= stackStart && line.normalizedStart < stackEnd);
  const candidateRows = [];
  const rowPattern = /^\| Agent Handoff Kit template version \| ([^|\n]+) \| [^|\n]+ \|$/u;
  for (const line of stackLines) {
    const match = rowPattern.exec(line.text);
    if (!match) continue;
    const version = match[1].trim();
    if (!isStableSemver(version)) return null;
    candidateRows.push({
      version,
      row: line.text,
      rowStart: line.start,
      rowEnd: line.end
    });
  }
  const versionLabelRows = stackLines.filter((line) => line.text.startsWith("| Agent Handoff Kit template version |"));
  if (versionLabelRows.length !== candidateRows.length || candidateRows.length !== 1) return null;
  const [row] = candidateRows;
  return { version: row.version, row: row.row, rowStart: row.rowStart, rowEnd: row.rowEnd };
}

export function markdownVisibleLinesOutsideHiddenBlocks(text) {
  const value = String(text);
  const normalized = value.replace(/\r\n/g, "\n");
  const lines = normalized.split("\n");
  const result = [];
  let offset = 0;
  let fence = null;
  let inComment = false;
  for (let index = 0; index < lines.length; index += 1) {
    const line = lines[index];
    if (inComment) {
      if (line.includes("-->")) inComment = false;
      offset += line.length + 1;
      continue;
    }
    const fenceMatch = /^\s{0,3}(`{3,}|~{3,})(?![`~])(.*)$/u.exec(line);
    const fenceRun = fenceMatch?.[1] ?? null;
    if (fence) {
      if (
        fenceRun
        && fenceRun[0] === fence.char
        && fenceRun.length >= fence.length
        && /^\s*$/u.test(fenceMatch?.[2] ?? "")
      ) {
        fence = null;
      }
      offset += line.length + 1;
      continue;
    }
    if (fenceRun) {
      fence = { char: fenceRun[0], length: fenceRun.length };
      offset += line.length + 1;
      continue;
    }
    const commentStart = line.indexOf("<!--");
    if (commentStart >= 0) {
      if (line.indexOf("-->", commentStart + 4) < 0) inComment = true;
      offset += line.length + 1;
      continue;
    }
    result.push({
      text: line,
      line: index,
      normalizedStart: offset,
      normalizedEnd: offset + line.length,
      start: originalOffsetForNormalizedOffset(value, offset),
      end: originalOffsetForNormalizedOffset(value, offset + line.length)
    });
    offset += line.length + 1;
  }
  return result;
}

function originalOffsetForNormalizedOffset(text, normalizedOffset) {
  let original = 0;
  let normalized = 0;
  while (original < text.length && normalized < normalizedOffset) {
    if (text[original] === "\r" && text[original + 1] === "\n") {
      original += 2;
      normalized += 1;
    } else {
      original += 1;
      normalized += 1;
    }
  }
  return original;
}

function isStableSemver(value) {
  return /^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)$/u.test(String(value));
}
