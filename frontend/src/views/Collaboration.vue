<template>
    <div class="container-fluid text-dark text-center py-4 mb-2">
    <h2>社区治理评估</h2>
  </div>

    <div class="container w-75 py-4">

    <div v-if="loading" class="text-center">加载中...</div>
    
    <div v-if="result">
      <p class="text-secondary text-center">评分最后更新：{{ date }}</p>
      <RecursiveList :data="scores" />
    </div>
  </div>

</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import RecursiveList from '../components/RecursiveList.vue'

const result = ref({})
const date = ref({})
const scores = ref(null)
const loading = ref(true)

function addAveragesPreserveLeaves(node) {
  if (typeof node === 'number') {
    return node // 保持叶子为数字
  }

  const result = {}
  let sum = 0
  let count = 0

  for (const key in node) {
    const child = node[key]
    const processed = addAveragesPreserveLeaves(child)
    result[key] = processed

    // 只统计数字，表示是叶子
    const score = typeof processed === 'number'
      ? processed
      : (processed.average ?? null)

    if (score !== null && !isNaN(score)) {
      sum += score
      count++
    }
  }

  result.average = count > 0 ? +(sum / count).toFixed(2) : null
  return result
}

const analyzeRules = async () => {
  try {
    const res = await axios.get('http://localhost:8000/governance/')
    result.value = res.data

    date.value = result.value.date
    scores.value = addAveragesPreserveLeaves(result.value.scores)
    
  } catch (error) {
    console.error(error);
    alert('展示失败')
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  analyzeRules()
})

</script>