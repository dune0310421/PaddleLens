<template>

  <div class="container-fluid text-dark text-center py-4 mb-2">
    <h2>开发者能力度量</h2>
  </div>

  <div class="container-fluid py-2 mb-3 w-50">
    <div class="row align-items-center g-2">
      <div class="col-auto">
        <label for="githubUser" class="col-form-label">请输入 GitHub 用户名：</label>
      </div>
      <div class="col">
        <div class="input-group">
          <input
            v-model="githubUser"
            @keyup.enter="analyzeSkills"
            id="githubUser"
            class="form-control shadow-none"
            placeholder="例如 torvalds"
          />
          <button @click="analyzeSkills" class="btn btn-light border">分析</button>
        </div>
      </div>
    </div>
  </div>

  <div class="container-fluid py-2 mb-5 w-75">
    
    <div v-if="loading" class="text-center">分析中...</div>

    <div v-if="result">
      <h3 class="text-center border-top mb-3 py-3 my-3">{{ result.username }}的能力度量结果</h3>

      <!-- 基本信息 -->
      <h5 class="text-center bg-light mb-3 py-3 my-3">基本信息</h5>
      <div class="row mb-3">
        <div class="col-md-3 mb-2">
          <label class="form-label"><strong>用户名</strong></label>
          <div>{{ result.basic_info.username || '无' }}</div>
        </div>
        <div class="col-md-3 mb-2">
          <label class="form-label"><strong>昵称</strong></label>
          <div>{{ result.basic_info.name || '无' }}</div>
        </div>
        <div class="col-md-3 mb-2">
          <label class="form-label"><strong>邮箱</strong></label>
          <div>{{ result.basic_info.email || '无' }}</div>
        </div>
        <div class="col-md-3 mb-2">
          <label class="form-label"><strong>公司</strong></label>
          <div>{{ result.basic_info.company || '无' }}</div>
        </div>

        <div class="col-md-3 mb-2">
          <label class="form-label"><strong>位置</strong></label>
          <div>{{ result.basic_info.location || '无' }}</div>
        </div>
        <div class="col-md-3 mb-2">
          <label class="form-label"><strong>创建日期</strong></label>
          <div>{{ result.basic_info.created_at || '无' }}</div>
        </div>
        <div class="col-md-3 mb-2">
          <label class="form-label"><strong>关注数量</strong></label>
          <div>{{ result.basic_info.following || 0 }}</div>
        </div>
        <div class="col-md-3 mb-2">
          <label class="form-label"><strong>粉丝数量</strong></label>
          <div>{{ result.basic_info.followers || 0 }}</div>
        </div>
      </div>

      <!-- 开发经验 -->
      <h5 class="text-center bg-light mb-3 py-3 my-3">在飞桨中的开发经验</h5>
      <div class="container-fluid border-bottom">
        <div class="row">
          <div class="col-md-4 mb-2">
            <p><strong>Repos：</strong>{{ result.experience.data.paddle_repos_cnt || 0 }}</p>
          </div>
          <div class="col-md-4 mb-2">
            <p><strong>Commits：</strong>{{ result.experience.data.commits_cnt || 0 }}</p>
          </div>
          <div class="col-md-4 mb-2">
            <p><strong>PRs：</strong>{{ result.experience.data.prs_cnt || 0 }}</p>
          </div>

          <div class="col-md-4 mb-2">
            <p><strong>Issues：</strong>{{ result.experience.data.issues_cnt || 0 }}</p>
          </div>
          <div class="col-md-4 mb-2">
            <p><strong>Comments：</strong>{{ result.experience.data.comments_cnt || 0 }}</p>
          </div>
          <div class="col-md-4 mb-2">
            <p><strong>Reviews：</strong>{{ result.experience.data.reviews_cnt || 0 }}</p>
          </div>
        </div>
      </div>

      <div class="container-fluid border-bottom py-3 my-3">
        <h6 class="mb-3">>在飞桨的Merge权限</h6>
        <div class=""> 拥有merge权限的仓库数: {{ result.experience.data.repos_can_merge_cnt || 0 }}，分别为：</div>
        <ul>
          <li v-for="repo in result.experience.data.repos_can_merge" :key="repo">{{ repo }}</li>
        </ul>
      </div>

      <div class="container-fluid border-bottom py-3 my-3">
        <h6 class="mb-3"> >贡献数量Top 5的项目</h6>
        <div class="img-fluid d-block mx-auto" ref="plot_fig_repo_contrib" style="width: 100%; height: 80%;"></div>
      </div>

      <div class="container-fluid py-3 my-3">
        <h6 class="mb-3"> >最近一年的贡献</h6>
        <div class="img-fluid d-block mx-auto" ref="plot_fig_recent_contrib" style="width: 100%; height: 80%;"></div>
      </div>

      <!-- 硬技能 -->
      <h5 class="text-center bg-light mb-3 py-3 my-3">硬技能</h5>
      <div class="container-fluid border-bottom py-3 my-3">
        <h6 class="mb-3"> >编程语言使用能力 </h6>
        <div ref="plot_fig_lang" style="width: 100%; height: 80%;"></div>
      </div>
      <div class="container-fluid border-bottom py-3 my-3">
        <h6 class="mb-3"> >领域能力 </h6>
        <img :src="'data:image/png;base64,' + result.hardskill.fig_domain_bytes" class="img-fluid d-block mx-auto" alt="领域能力图" style="width: 500px;" />
      </div>

      <div class="container-fluid py-3 my-3">
        <h6 class="mb-3"> >问题解决能力 </h6>
        <div ref="plot_fig_solving" class="img-fluid d-block mx-auto" style="width: 100%; height: 80%;"></div>
      </div>

      <!-- 软技能 -->
      <h5 class="text-center bg-light mb-3 py-3 my-3">软技能</h5>
      <div class="container-fluid border-bottom py-3 my-3">
        <h6 class="mb-3"> >责任心 </h6>
        <div class="row mb-3">
          <div class="col-md-6 mb-2">
            <div ref="plot_fig_consistency" class="img-fluid d-block mx-auto" style="width: 100%; height: 50%;"></div>
          </div>
          <div class="col-md-6 mb-2">
            <div ref="plot_fig_activeness" class="img-fluid d-block mx-auto" style="width: 100%; height: 50%;"></div>
          </div>
        </div>
      </div>

      <div class="container-fluid border-bottom py-3 my-3">
        <h6 class="mb-3"> >时间管理能力 </h6>
        在 {{ result.softskill.time_mgmt.max_active_month_start || "-" }} 到 {{ result.softskill.time_mgmt.max_active_month_end
          || "-" }} 两个月内，总共在{{ result.softskill.time_mgmt.active_projects.length || 0 }}个项目中贡献了
        {{ result.softskill.time_mgmt.commit_count || 0 }}个commit。这些项目分别是
        <ul>
          <li v-for="repo in result.softskill.time_mgmt.active_projects" :key="repo">{{ repo }}</li>
        </ul>
      </div>

      <div class="container-fluid py-3 my-3">
        <h6> 沟通能力 </h6>
        <p>沟通能力总分为 {{ result.softskill.comm_score || 0 }} (满分100)</p>
        <div ref="plot_fig_comm" style="width: 100%; height: 80%;"></div>
      </div>

    </div>
  </div>

</template>

<script>
import axios from 'axios'
import Plotly from 'plotly.js-dist-min'

export default {
  name: 'App',
  data() {
    return {
      githubUser: '',
      result: null,
      loading: false,
    }
  },
  methods: {
    async analyzeSkills() {
      if (!this.githubUser.trim()) {
        alert('请输入用户');
        return;
      }

      this.result = null;
      this.loading = true;

      try {

        const res = await axios.post('http://localhost:8000/analyze/', {
          github_user: this.githubUser
        })
        this.result = res.data  // 结果对象
        // this.resultRaw = JSON.stringify(res.data, null, 2)

        // 画图：Plotly.newPlot(容器, 数据, 布局)
        const plot_fig_repo_contrib_Data = this.result.experience?.fig_repo_contrib?.data || []
        const plot_fig_repo_contrib_Layout = this.result.experience?.fig_repo_contrib?.layout || {}
        const plot_fig_recent_contrib_Data = this.result.experience?.fig_recent_contrib?.data || []
        const plot_fig_recent_contrib_Layout = this.result.experience?.fig_recent_contrib?.layout || {}
        const plot_fig_lang_Data = this.result.hardskill?.fig_lang?.data || []
        const plot_fig_lang_Layout = this.result.hardskill?.fig_lang?.layout || {}
        const plot_fig_solving_Data = this.result.hardskill?.fig_solving?.data || []
        const plot_fig_solving_Layout = this.result.hardskill?.fig_solving?.layout || {}
        const plot_fig_consistency_Data = this.result.softskill?.fig_consistency?.data || []
        const plot_fig_consistency_Layout = this.result.softskill?.fig_consistency?.layout || {}
        const plot_fig_activeness_Data = this.result.softskill?.fig_activeness?.data || []
        const plot_fig_activeness_Layout = this.result.softskill?.fig_activeness?.layout || {}
        const plot_fig_comm_Data = this.result.softskill?.fig_comm?.data || []
        const plot_fig_comm_Layout = this.result.softskill?.fig_comm?.layout || {}

        console.log('图表 DATA:', plot_fig_lang_Data)
        console.log('图表 LAYOUT:', plot_fig_lang_Layout)

        // 等 DOM 渲染好了之后再画图
        this.$nextTick(() => {
          Plotly.newPlot(this.$refs.plot_fig_repo_contrib, plot_fig_repo_contrib_Data, plot_fig_repo_contrib_Layout)
          Plotly.newPlot(this.$refs.plot_fig_recent_contrib, plot_fig_recent_contrib_Data, plot_fig_recent_contrib_Layout)
          Plotly.newPlot(this.$refs.plot_fig_lang, plot_fig_lang_Data, plot_fig_lang_Layout)
          Plotly.newPlot(this.$refs.plot_fig_solving, plot_fig_solving_Data, plot_fig_solving_Layout)
          Plotly.newPlot(this.$refs.plot_fig_consistency, plot_fig_consistency_Data, plot_fig_consistency_Layout)
          Plotly.newPlot(this.$refs.plot_fig_activeness, plot_fig_activeness_Data, plot_fig_activeness_Layout)
          Plotly.newPlot(this.$refs.plot_fig_comm, plot_fig_comm_Data, plot_fig_comm_Layout)
        });

      } catch (err) {
        console.error(err)
        alert('分析失败，请检查服务器或用户名')
      } finally {
        this.loading = false
      }
    }
  }
}
</script>