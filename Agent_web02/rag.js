const kbData = {
  学业知识库: ["本科培养方案.pdf", "选课指南.docx", "学分认定细则.md"],
  活动知识库: ["校园文化活动日历.xlsx", "社团活动申请流程.pdf", "志愿服务项目清单.md"],
  党团知识库: ["入党流程说明.pdf", "团支部工作手册.docx", "组织生活记录模板.md"],
  就业知识库: ["实习信息汇总.xlsx", "秋招企业名单.pdf", "简历与面试指导手册.docx"],
  行政知识库: ["请假与销假流程.pdf", "奖助学金管理办法.docx", "宿舍管理条例.md"]
};

const kbGrid = document.getElementById("kbGrid");
const docList = document.getElementById("docList");

Object.keys(kbData).forEach((kbName) => {
  const item = document.createElement("div");
  item.className = "kb-item";
  item.innerHTML = `<strong>${kbName}</strong><div class="subtext top-gap">点击查看文档</div>`;
  item.addEventListener("click", () => {
    docList.innerHTML = `<h3 class="doc-title">${kbName} 文档</h3>`;
    kbData[kbName].forEach((doc) => {
      const docNode = document.createElement("div");
      docNode.className = "doc";
      docNode.textContent = `📄 ${doc}`;
      docList.appendChild(docNode);
    });
  });
  kbGrid.appendChild(item);
});
