<%* let title = tp.file.title
  if (title.startsWith("Untitled")) {
    title = await tp.system.prompt("Title");
    await tp.file.rename(title);
  } 
-%>
<%*
  let result = title.replace(/-/g, ' ')
  result = result.charAt(0).toUpperCase() + result.slice(1);
  tR += "---"
%>
title:  <%* tR += "\"" + result + "\"" %>
tags:
<% tp.file.cursor(1) %>
programming-languagues:
created: <% tp.date.now("YYYY-MM-DD") %>
---
# <%* tR += result %>
---