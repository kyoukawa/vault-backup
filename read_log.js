const fs = require("fs");
const path = "C:\Users\chuan\Documents\知识库\decoded\decode_log.txt";
const content = fs.readFileSync(path, "utf-8");
console.log(content);
