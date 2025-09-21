<template>
  <div class="p-3">
    <div v-for="(value, key) in data" :key="key" class="list-group-item m-1">
      <!-- 渲染每一个指标 -->
      <div v-if="key !== 'average'" class="d-flex justify-content-between align-items-center p-3 border-0 rounded" style="background-color: #F0F3F5;">
        <div>
          <!-- 折叠按钮，仅当是对象时显示 -->
          <button v-if="isObject(value)" class="btn btn-sm btn-link p-0 me-2" @click="toggleCollapse(key)">
            <span>{{ ensureCollapse(key) ? '▼' : '▶' }}</span>
          </button>
          <!-- 名称和描述 -->
          <strong>{{ nameMap[key] || key }}</strong>
          <small class="text-muted ms-2">{{ descMap[key] || '' }}</small>
        </div>
        <!-- 得分 -->
        <span v-if="isObject(value) && value?.average !== undefined"
              :class="['badge', 'rounded-pill', scoreColor(value.average)]">
          {{ value.average }}
        </span>
        <span v-if="!isObject(value)"
              :class="['badge', 'rounded-pill', scoreColor(value)]">
          {{ value }}
        </span>
      </div>

      <!-- 递归渲染，需要是对象且处于展开状态 -->
      <div v-if="isObject(value) && ensureCollapse(key)" class="ms-3 me-3 border-start">
        <RecursiveList :data="value" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { defineProps, ref } from 'vue'

const props = defineProps({
  data: {
    type: Object,
    required: true
  }
})

// 中文标题映射
const nameMap = {
  usage: '项目使用',
  installation_guide: '安装指南',
  usage_guide: '使用指南',
  security_policy: '安全策略',
  license: '许可证',
  
  contribution: '社区贡献',
  contribution_guidelines: '贡献指引与准备',
  contribution_types: '贡献类型',
  cla: '贡献者许可协议（CLA）',
  communication_way: '沟通方式',
  mentorship: '导师机制',
  local_environment_setup: '本地环境构建',

  contribution_submission: '贡献撰写与提交',
    writing_standards: '贡献编写规范',
  // completeness: '结构完整性',
  // quality: '内容质量',
  // style: '格式规范',
  submission_standards: '提交规范',
  // size: '粒度',
  // description: '描述',
  code_of_conduct: '行为准则（CoC）',

  contribution_acceptance: '贡献接收',
  review_standards: '评审标准',
  review_process: '评审流程',
  ci_description: 'CI说明',

  organization: '项目组织与维护',
  role_management: '角色管理',
  role_definition: '角色定义',
  role_assignment_process: '分配流程',
  role_assignment_standards: '职责说明',
  release_management: '版本管理',
  // release_plan: '版本发布计划',
  // release_steps: '版本发布步骤',
  // release_notes: '版本发布说明'
}
// 中文描述映射
const descMap = {
  usage: '项目安装和使用的步骤与要求，保障用户在了解规则与条件的前提下顺利运行系统。',
  installation_guide: '项目安装步骤',
  usage_guide: '项目使用步骤',
  security_policy: '项目安全问题的定义、汇报流程以及安全使用建议',
  license: '项目的开源许可协议',
  
  contribution: '项目贡献的流程与规范，保障贡献者在了解规则与条件的前提下顺利参与项目开发。',
  contribution_guidelines: '贡献机会、贡献方式和贡献支持',
  contribution_types: '可选择的贡献类型',
  cla: '在贡献前需要签署的许可协议',
  communication_way: '交流渠道与反馈机制',
  mentorship: '项目为贡献者提供的人员指导和支持',
  local_environment_setup: '涉及对操作系统、依赖工具、编译器等开发运行时环境的引导。',
  
  contribution_submission: '贡献撰写与提交的步骤与规范',
  writing_standards: '贡献内容在内容完整性、质量和格式上的标准',
  // completeness: '结构完整性',
  // quality: '内容质量',
  // style: '格式规范',
  submission_standards: '提交项（PR）的粒度和描述规范',
  code_of_conduct: '社区协作需要满足的行为准则',
  // size: '粒度',
  // description: '描述',

  contribution_acceptance: '贡献接收步骤与规范',
  review_standards: '对贡献进行评审时需要考虑的内容',
  review_process: '代码评审的步骤',
  ci_description: 'CI检查项、执行环境与失败解决方案',

  organization: '项目的治理结构设计与发布流程安排，保障社区运行的稳定性、透明度与长期演进。',
  role_management: '社区各类角色的设置与管理',
  role_definition: '社区中各类角色的定义与职责描述',
  role_assignment_process: '角色分配的流程与规范',
  role_assignment_standards: '角色分配的标准与准则',
  release_management: '项目版本发布的计划、步骤与版本发布说明',
  // release_plan: '版本发布计划',
  // release_steps: '版本发布',
  // release_notes: '版本发布说明'
}

// 判断是否为对象（非叶子节点）
const isObject = (val) => typeof val === 'object' && val !== null

// 根据评分返回不同颜色
const scoreColor = (score) => {
  if (score < 2.0) return 'bg-danger text-white'
  if (score < 4.0) return 'bg-warning text-white'
  return 'bg-success text-white'
}

// 控制折叠状态（按 key 存储）
const collapsedKeys = ref({})
//查询展开状态
const ensureCollapse = (key) => {
  if (!(key in collapsedKeys.value)) {
    collapsedKeys.value[key] = false
  }
  return collapsedKeys.value[key]
}
// 折叠/展开切换
const toggleCollapse = (key) => {
  collapsedKeys.value[key] = !collapsedKeys.value[key]
}

</script>

<style scoped>
button {
  color: black;
  text-decoration: none;
}
</style>