const CITY_PRESETS = {
  xiamen: {
    key: "xiamen",
    city: "厦门",
    district: "思明区",
    label: "厦门 · 思明区",
    lat: 24.4798,
    lng: 118.0894
  },
  shanghai: {
    key: "shanghai",
    city: "上海",
    district: "黄浦区",
    label: "上海 · 黄浦区",
    lat: 31.2304,
    lng: 121.4737
  },
  shenzhen: {
    key: "shenzhen",
    city: "深圳",
    district: "南山区",
    label: "深圳 · 南山区",
    lat: 22.5431,
    lng: 114.0579
  },
  beijing: {
    key: "beijing",
    city: "北京",
    district: "朝阳区",
    label: "北京 · 朝阳区",
    lat: 39.9042,
    lng: 116.4074
  }
};

const roleConfig = {
  enthusiast: {
    label: "健身爱好者",
    short: "训练者",
    intro: "完善你的训练画像、目标和常驻城市，系统会根据你的定位推荐附近场馆和教练。",
    fields: [
      { name: "avatar_file", label: "头像", type: "file", required: false, accept: "image/*" },
      { name: "name", label: "昵称 / 姓名", type: "text", required: true, placeholder: "例如：小鹿训练日记" },
      { name: "phone", label: "手机号", type: "tel", required: true, placeholder: "请输入手机号" },
      { name: "gender", label: "性别", type: "select", required: true, options: ["男", "女"] },
      { name: "height_cm", label: "身高（cm）", type: "number", required: true, placeholder: "例如：172" },
      { name: "weight_kg", label: "体重（kg）", type: "number", required: true, placeholder: "例如：64.5" },
      { name: "city", label: "所在城市", type: "text", required: false, placeholder: "例如：厦门" },
      { name: "location", label: "常驻定位", type: "text", required: false, placeholder: "例如：思明区软件园" },
      {
        name: "level",
        label: "健身程度",
        type: "select",
        required: false,
        options: ["新手入门", "规律训练", "进阶塑形", "高阶力量"]
      },
      { name: "goal", label: "训练目标", type: "textarea", required: false, placeholder: "例如：减脂 6kg，改善体态" },
      { name: "intro", label: "主页简介", type: "textarea", required: false, placeholder: "例如：每周四练，欢迎一起打卡" }
    ]
  },
  gym: {
    label: "健身房",
    short: "场馆",
    intro: "填写门店定位、设备、营业信息与照片，提交后会自动生成你的健身房主页。",
    fields: [
      { name: "avatar_file", label: "门店头像 / 品牌头像", type: "file", required: false, accept: "image/*" },
      { name: "gym_name", label: "场馆名称", type: "text", required: true, placeholder: "例如：FitLab 厦门万象城店" },
      { name: "contact_name", label: "联系人", type: "text", required: false, placeholder: "请输入负责人姓名" },
      { name: "phone", label: "联系电话", type: "tel", required: true, placeholder: "请输入联系电话" },
      { name: "city", label: "所在城市", type: "text", required: false, placeholder: "例如：厦门" },
      { name: "location", label: "门店定位", type: "text", required: false, placeholder: "例如：思明区湖滨东路 99 号" },
      { name: "hours", label: "营业时间", type: "text", required: false, placeholder: "例如：06:00 - 23:00 / 24h" },
      { name: "price", label: "会员价格", type: "text", required: false, placeholder: "例如：¥119/月起" },
      { name: "facilities", label: "设备与设施", type: "textarea", required: false, placeholder: "例如：深蹲架、跑步机、团课教室、恢复区" },
      { name: "intro", label: "主页简介", type: "textarea", required: false, placeholder: "例如：24h 营业，器械区和团课区齐备" },
      { name: "equipment_photos", label: "设备照片", type: "file", required: false, multiple: true }
    ]
  },
  coach: {
    label: "健身教练",
    short: "教练",
    intro: "填写服务区域、擅长领域、从业时间与资质，提交后会自动生成你的教练主页。",
    fields: [
      { name: "avatar_file", label: "教练头像", type: "file", required: false, accept: "image/*" },
      { name: "name", label: "姓名", type: "text", required: true, placeholder: "例如：刘晓敏" },
      { name: "phone", label: "手机号", type: "tel", required: true, placeholder: "请输入手机号" },
      { name: "city", label: "服务城市", type: "text", required: false, placeholder: "例如：厦门" },
      { name: "location", label: "服务区域", type: "text", required: false, placeholder: "例如：思明区 / 湖里区" },
      { name: "specialties", label: "擅长领域", type: "textarea", required: false, placeholder: "例如：减脂塑形、力量提升、体态纠正" },
      { name: "years", label: "从业时间（年）", type: "number", required: false, placeholder: "例如：5" },
      { name: "price", label: "课时费", type: "text", required: false, placeholder: "例如：¥260/小时" },
      { name: "certifications", label: "资质证书", type: "textarea", required: false, placeholder: "例如：NASM、ACE、CBBA" },
      { name: "intro", label: "主页简介", type: "textarea", required: false, placeholder: "例如：擅长动作纠正和一对一减脂计划" },
      { name: "cert_files", label: "证书照片", type: "file", required: false, multiple: true }
    ]
  }
};

const CHECKIN_SPORTS = [
  { id: "run", label: "户外跑步", hint: "户外自由跑", icon: "跑", category: "我的运动", metricKey: "run" },
  { id: "outdoor-walk", label: "户外行走", hint: "轻松走 / 快走", icon: "走", category: "我的运动", metricKey: "walk" },
  { id: "rope", label: "跳绳", hint: "燃脂爆发", icon: "跳", category: "我的运动", metricKey: "rope" },
  { id: "cycling", label: "室内骑行", hint: "动感单车", icon: "骑", category: "我的运动", metricKey: "cycling" },
  { id: "outdoor-cycling", label: "户外骑行", hint: "公路 / 城市骑行", icon: "骑", category: "我的运动", metricKey: "cycling" },
  { id: "treadmill", label: "室内跑步", hint: "跑步机训练", icon: "跑", category: "我的运动", metricKey: "run" },
  { id: "stairs", label: "爬楼梯", hint: "提升心肺", icon: "梯", category: "跑走骑运动", metricKey: "stairs" },
  { id: "indoor-walk", label: "室内行走", hint: "恢复活动", icon: "走", category: "跑走骑运动", metricKey: "walk" },
  { id: "hiking", label: "徒步", hint: "耐力拉练", icon: "徒", category: "跑走骑运动", metricKey: "hike" },
  { id: "trail-run", label: "越野跑", hint: "坡度与变速", icon: "越", category: "跑走骑运动", metricKey: "hike" },
  { id: "badminton", label: "羽毛球", hint: "灵敏步伐", icon: "羽", category: "球类运动", metricKey: "ball" },
  { id: "football", label: "足球", hint: "跑动对抗", icon: "足", category: "球类运动", metricKey: "ball" },
  { id: "basketball", label: "篮球", hint: "力量与爆发", icon: "篮", category: "球类运动", metricKey: "ball" },
  { id: "pingpong", label: "乒乓球", hint: "反应速度", icon: "乒", category: "球类运动", metricKey: "ball" },
  { id: "tennis", label: "网球", hint: "有氧耐力", icon: "网", category: "球类运动", metricKey: "ball" },
  { id: "volleyball", label: "排球", hint: "弹跳协调", icon: "排", category: "球类运动", metricKey: "ball" },
  { id: "bowling", label: "保龄球", hint: "轻竞技休闲", icon: "保", category: "球类运动", metricKey: "leisure" },
  { id: "golf", label: "高尔夫球", hint: "挥杆练习", icon: "高", category: "球类运动", metricKey: "leisure" },
  { id: "yoga", label: "瑜伽", hint: "舒展与恢复", icon: "瑜", category: "室内运动", metricKey: "yoga" },
  { id: "hiit", label: "HIIT", hint: "高强度燃脂", icon: "燃", category: "室内运动", metricKey: "hiit" },
  { id: "strength", label: "传统力量训练", hint: "器械 / 自由重量", icon: "力", category: "室内运动", metricKey: "strength" },
  { id: "accessory", label: "小器械", hint: "壶铃 / 弹力带", icon: "械", category: "室内运动", metricKey: "accessory" },
  { id: "cardio-mix", label: "混合有氧", hint: "持续心肺训练", icon: "氧", category: "室内运动", metricKey: "cardio" },
  { id: "aerobics", label: "健身操", hint: "节奏训练", icon: "操", category: "室内运动", metricKey: "dance" },
  { id: "dance", label: "舞蹈", hint: "律动训练", icon: "舞", category: "室内运动", metricKey: "dance" },
  { id: "zumba", label: "尊巴", hint: "燃脂律动", icon: "尊", category: "室内运动", metricKey: "dance" },
  { id: "pilates", label: "普拉提", hint: "核心稳定", icon: "普", category: "室内运动", metricKey: "pilates" },
  { id: "boxing", label: "拳击", hint: "上肢爆发", icon: "拳", category: "室内运动", metricKey: "boxing" },
  { id: "fighting", label: "格斗", hint: "对抗训练", icon: "格", category: "室内运动", metricKey: "boxing" },
  { id: "ballet", label: "芭蕾", hint: "控制与平衡", icon: "芭", category: "室内运动", metricKey: "dance" },
  { id: "elliptical", label: "椭圆机", hint: "低冲击心肺", icon: "椭", category: "室内运动", metricKey: "machine" },
  { id: "rowing", label: "划船机", hint: "全身协调", icon: "划", category: "室内运动", metricKey: "machine" },
  { id: "stepper", label: "踏步机", hint: "下肢耐力", icon: "踏", category: "室内运动", metricKey: "machine" },
  { id: "stair-machine", label: "台阶机", hint: "爬升模拟", icon: "台", category: "室内运动", metricKey: "machine" },
  { id: "frisbee", label: "飞盘", hint: "户外休闲", icon: "盘", category: "休闲运动", metricKey: "leisure" },
  { id: "roller", label: "轮滑", hint: "平衡滑行", icon: "轮", category: "休闲运动", metricKey: "leisure" },
  { id: "skateboard", label: "滑板", hint: "核心平衡", icon: "板", category: "休闲运动", metricKey: "leisure" },
  { id: "hula", label: "呼啦圈", hint: "轻松活动", icon: "圈", category: "休闲运动", metricKey: "leisure" },
  { id: "swim", label: "泳池游泳", hint: "标准泳池", icon: "泳", category: "水中运动", metricKey: "swim" },
  { id: "outdoor-swim", label: "户外游泳", hint: "开放水域", icon: "泳", category: "水中运动", metricKey: "swim" },
  { id: "surf", label: "冲浪", hint: "核心控制", icon: "冲", category: "水中运动", metricKey: "surf" },
  { id: "trampoline", label: "蹦床", hint: "跳跃协调", icon: "蹦", category: "专业运动", metricKey: "extreme" },
  { id: "skating", label: "滑冰", hint: "平衡稳定", icon: "冰", category: "专业运动", metricKey: "extreme" },
  { id: "skiing", label: "滑雪", hint: "下肢控制", icon: "雪", category: "专业运动", metricKey: "extreme" },
  { id: "fencing", label: "击剑", hint: "敏捷对抗", icon: "剑", category: "专业运动", metricKey: "ball" },
  { id: "archery", label: "射箭", hint: "稳定专注", icon: "弓", category: "专业运动", metricKey: "martial" },
  { id: "equestrian", label: "马术", hint: "核心稳定", icon: "马", category: "专业运动", metricKey: "leisure" },
  { id: "climbing", label: "攀岩", hint: "抓握力量", icon: "岩", category: "专业运动", metricKey: "extreme" },
  { id: "tai-chi", label: "太极", hint: "呼吸与平衡", icon: "太", category: "武术运动", metricKey: "martial" },
  { id: "wing-chun", label: "咏春", hint: "节奏与出拳", icon: "咏", category: "武术运动", metricKey: "martial" },
  { id: "wuqinxi", label: "五禽戏", hint: "传统养生", icon: "五", category: "武术运动", metricKey: "martial" },
  { id: "meditation", label: "冥想", hint: "呼吸放松", icon: "静", category: "其他运动", metricKey: "meditation" }
];

const CHECKIN_SPORT_SECTIONS = [
  { label: "我的运动", ids: ["run", "outdoor-walk", "rope", "cycling", "outdoor-cycling", "treadmill"] },
  { label: "跑走骑运动", ids: ["stairs", "indoor-walk", "hiking", "trail-run"] },
  { label: "球类运动", ids: ["badminton", "football", "basketball", "pingpong", "tennis", "volleyball", "bowling", "golf"] },
  { label: "室内运动", ids: ["yoga", "hiit", "strength", "accessory", "cardio-mix", "aerobics", "dance", "zumba", "pilates", "boxing", "fighting", "ballet", "elliptical", "rowing", "stepper", "stair-machine"] },
  { label: "休闲运动", ids: ["frisbee", "roller", "skateboard", "hula"] },
  { label: "水中运动", ids: ["swim", "outdoor-swim", "surf"] },
  { label: "专业运动", ids: ["trampoline", "skating", "skiing", "fencing", "archery", "equestrian", "climbing"] },
  { label: "武术运动", ids: ["tai-chi", "wing-chun", "wuqinxi"] },
  { label: "其他运动", ids: ["meditation"] }
];

const CHECKIN_SPORT_METRICS = {
  run: { met: 8.5, paceKmh: 8.4, impact: "high" },
  "outdoor-walk": { met: 4.8, paceKmh: 5.8, impact: "high" },
  rope: { met: 11.8, paceKmh: 0, impact: "high" },
  cycling: { met: 7.0, paceKmh: 19, impact: "low" },
  "outdoor-cycling": { met: 6.8, paceKmh: 18, impact: "low" },
  treadmill: { met: 8.3, paceKmh: 8.1, impact: "high" },
  stairs: { met: 8.8, paceKmh: 0, impact: "high" },
  "indoor-walk": { met: 3.8, paceKmh: 4.8, impact: "high" },
  hiking: { met: 6.0, paceKmh: 4.7, impact: "high" },
  "trail-run": { met: 9.0, paceKmh: 7.4, impact: "high" },
  badminton: { met: 5.5, paceKmh: 0, impact: "high" },
  football: { met: 8.0, paceKmh: 0, impact: "high" },
  basketball: { met: 7.5, paceKmh: 0, impact: "high" },
  pingpong: { met: 4.0, paceKmh: 0, impact: "high" },
  tennis: { met: 7.3, paceKmh: 0, impact: "high" },
  volleyball: { met: 4.0, paceKmh: 0, impact: "high" },
  bowling: { met: 3.8, paceKmh: 0, impact: "low" },
  golf: { met: 4.5, paceKmh: 3.6, impact: "high" },
  yoga: { met: 2.8, paceKmh: 0, impact: "low" },
  hiit: { met: 8.0, paceKmh: 0, impact: "mixed" },
  strength: { met: 5.5, paceKmh: 0, impact: "mixed" },
  accessory: { met: 4.8, paceKmh: 0, impact: "mixed" },
  "cardio-mix": { met: 6.8, paceKmh: 0, impact: "mixed" },
  aerobics: { met: 6.5, paceKmh: 0, impact: "mixed" },
  dance: { met: 5.5, paceKmh: 0, impact: "mixed" },
  zumba: { met: 7.3, paceKmh: 0, impact: "mixed" },
  pilates: { met: 3.0, paceKmh: 0, impact: "low" },
  boxing: { met: 7.8, paceKmh: 0, impact: "high" },
  fighting: { met: 8.5, paceKmh: 0, impact: "high" },
  ballet: { met: 5.0, paceKmh: 0, impact: "mixed" },
  elliptical: { met: 5.0, paceKmh: 0, impact: "low" },
  rowing: { met: 7.0, paceKmh: 0, impact: "mixed" },
  stepper: { met: 8.8, paceKmh: 0, impact: "high" },
  "stair-machine": { met: 9.0, paceKmh: 0, impact: "high" },
  frisbee: { met: 3.0, paceKmh: 0, impact: "low" },
  roller: { met: 7.0, paceKmh: 0, impact: "mixed" },
  skateboard: { met: 5.0, paceKmh: 0, impact: "mixed" },
  hula: { met: 4.0, paceKmh: 0, impact: "mixed" },
  swim: { met: 6.0, paceKmh: 2.0, impact: "water" },
  "outdoor-swim": { met: 7.0, paceKmh: 2.3, impact: "water" },
  surf: { met: 5.0, paceKmh: 0, impact: "water" },
  trampoline: { met: 5.5, paceKmh: 0, impact: "high" },
  skating: { met: 7.0, paceKmh: 0, impact: "mixed" },
  skiing: { met: 7.0, paceKmh: 0, impact: "mixed" },
  fencing: { met: 6.0, paceKmh: 0, impact: "mixed" },
  archery: { met: 4.3, paceKmh: 0, impact: "low" },
  equestrian: { met: 5.5, paceKmh: 0, impact: "mixed" },
  climbing: { met: 8.0, paceKmh: 0, impact: "high" },
  "tai-chi": { met: 4.0, paceKmh: 0, impact: "low" },
  "wing-chun": { met: 5.5, paceKmh: 0, impact: "mixed" },
  wuqinxi: { met: 4.2, paceKmh: 0, impact: "low" },
  meditation: { met: 1.5, paceKmh: 0, impact: "low" }
};

const OUTDOOR_ROUTE_SPORT_IDS = new Set(["run", "outdoor-walk", "outdoor-cycling", "hiking", "trail-run"]);

const HEALTH_VIEW_MODES = [
  { id: "overview", label: "概览" },
  { id: "trends", label: "趋势" },
  { id: "all", label: "全部" }
];

const HEALTH_TREND_GROUPS = [
  {
    id: "run",
    label: "跑步",
    icon: "跑",
    sportIds: ["run", "treadmill", "trail-run"],
    metric: "distance",
    unit: "公里",
    accent: "#2cc58d",
    soft: "rgba(44, 197, 141, 0.16)"
  },
  {
    id: "walk",
    label: "行走",
    icon: "走",
    sportIds: ["outdoor-walk", "indoor-walk", "hiking"],
    metric: "distance",
    unit: "公里",
    accent: "#5b8cff",
    soft: "rgba(91, 140, 255, 0.14)"
  },
  {
    id: "cycling",
    label: "骑行",
    icon: "骑",
    sportIds: ["cycling", "outdoor-cycling"],
    metric: "distance",
    unit: "公里",
    accent: "#8d6dff",
    soft: "rgba(141, 109, 255, 0.15)"
  },
  {
    id: "yoga",
    label: "瑜伽",
    icon: "瑜",
    sportIds: ["yoga", "pilates"],
    metric: "duration",
    unit: "分钟",
    accent: "#a98af8",
    soft: "rgba(169, 138, 248, 0.15)"
  }
];

const OUTDOOR_ROUTE_TEMPLATES = {
  run: [
    [10, 63], [18, 46], [36, 34], [54, 37], [72, 32], [89, 40], [84, 58], [71, 73], [52, 81], [31, 78], [16, 70], [10, 63]
  ],
  "outdoor-walk": [
    [12, 61], [22, 49], [34, 40], [49, 38], [63, 44], [78, 47], [84, 60], [70, 68], [53, 72], [34, 71], [19, 66], [12, 61]
  ],
  "outdoor-cycling": [
    [8, 67], [16, 43], [36, 24], [61, 20], [85, 30], [92, 52], [82, 74], [60, 84], [34, 80], [17, 67], [8, 67]
  ],
  hiking: [
    [12, 70], [20, 55], [31, 45], [43, 32], [58, 28], [74, 34], [82, 50], [76, 66], [61, 76], [42, 79], [24, 75], [12, 70]
  ],
  "trail-run": [
    [10, 68], [19, 49], [30, 34], [47, 26], [65, 31], [82, 42], [88, 59], [78, 74], [59, 82], [37, 79], [20, 72], [10, 68]
  ]
};

const DEFAULT_MEDIA_LIMITS = Object.freeze({
  imageBytes: 10 * 1024 * 1024,
  videoBytes: 8 * 1024 * 1024,
  thumbnailBytes: 2 * 1024 * 1024,
});

const DEMO_ASSET_BASE = "assets/demo/";
const demoAsset = (name) => `${DEMO_ASSET_BASE}${name}`;

function createDemoImage(title, accentA, accentB) {
  const isCoachScene = /教练|私教|普拉提|塑形|动作|训练/.test(title || "");
  const svg = `
    <svg xmlns="http://www.w3.org/2000/svg" width="800" height="520" viewBox="0 0 800 520">
      <defs>
        <linearGradient id="wall" x1="0" x2="1" y1="0" y2="1">
          <stop offset="0%" stop-color="#f7f3ed"/>
          <stop offset="100%" stop-color="#dfe8ea"/>
        </linearGradient>
        <linearGradient id="floor" x1="0" x2="1" y1="0" y2="1">
          <stop offset="0%" stop-color="#efe4d5"/>
          <stop offset="100%" stop-color="#b9956a"/>
        </linearGradient>
        <linearGradient id="glass" x1="0" x2="1" y1="0" y2="1">
          <stop offset="0%" stop-color="#d8ebf4"/>
          <stop offset="100%" stop-color="#9fb7c4"/>
        </linearGradient>
        <filter id="soft" x="-20%" y="-20%" width="140%" height="140%">
          <feGaussianBlur stdDeviation="12"/>
        </filter>
      </defs>
      <rect width="800" height="520" rx="36" fill="url(#wall)"/>
      <rect y="338" width="800" height="182" fill="url(#floor)"/>
      <path d="M0 338h800" stroke="rgba(80,70,58,0.18)" stroke-width="4"/>
      <rect x="54" y="58" width="238" height="220" rx="20" fill="url(#glass)"/>
      <rect x="316" y="58" width="238" height="220" rx="20" fill="url(#glass)"/>
      <rect x="578" y="58" width="168" height="220" rx="20" fill="url(#glass)"/>
      <path d="M174 58v220M436 58v220M662 58v220M54 168h692" stroke="rgba(255,255,255,0.48)" stroke-width="8"/>
      <circle cx="94" cy="94" r="78" fill="${accentA}" opacity="0.16" filter="url(#soft)"/>
      <circle cx="694" cy="102" r="92" fill="${accentB}" opacity="0.16" filter="url(#soft)"/>
      ${
        isCoachScene
          ? `
            <rect x="86" y="292" width="256" height="24" rx="12" fill="#30343b"/>
            <rect x="134" y="238" width="28" height="96" rx="14" fill="#2b3038"/>
            <rect x="236" y="232" width="28" height="102" rx="14" fill="#2b3038"/>
            <circle cx="476" cy="202" r="48" fill="#e9b996"/>
            <path d="M429 196c8-44 36-68 70-57 24 8 36 29 36 55-34-20-65-20-106 2z" fill="#34261f"/>
            <path d="M398 360c10-74 42-114 82-114 50 0 88 44 98 114z" fill="${accentA}"/>
            <rect x="586" y="268" width="96" height="82" rx="18" fill="#30343b"/>
            <circle cx="606" cy="360" r="22" fill="#30343b"/>
            <circle cx="664" cy="360" r="22" fill="#30343b"/>
          `
          : `
            <rect x="90" y="244" width="120" height="126" rx="18" fill="#2d343d"/>
            <rect x="114" y="260" width="72" height="16" rx="8" fill="${accentA}"/>
            <rect x="128" y="296" width="16" height="62" rx="8" fill="#c8d1d8"/>
            <rect x="158" y="286" width="16" height="72" rx="8" fill="#c8d1d8"/>
            <rect x="264" y="306" width="176" height="22" rx="11" fill="#30343b"/>
            <circle cx="280" cy="342" r="28" fill="#30343b"/>
            <circle cx="424" cy="342" r="28" fill="#30343b"/>
            <rect x="508" y="238" width="142" height="164" rx="26" fill="#353c45"/>
            <rect x="534" y="268" width="90" height="96" rx="20" fill="#99a9b4"/>
            <rect x="626" y="282" width="42" height="16" rx="8" fill="${accentB}"/>
          `
      }
      <rect x="40" y="402" width="330" height="70" rx="24" fill="rgba(24,29,35,0.58)"/>
      <text x="70" y="447" fill="#fff" font-size="30" font-family="Arial, PingFang SC, sans-serif" font-weight="700">${title}</text>
    </svg>
  `;
  return `data:image/svg+xml;charset=UTF-8,${encodeURIComponent(svg)}`;
}

function createPortraitAvatar(options) {
  const {
    skin = "#f5c9a8",
    hair = "#41291c",
    shirt = "#1f2125",
    bgA = "#f4d6bf",
    bgB = "#c89266"
  } = options;

  const svg = `
    <svg xmlns="http://www.w3.org/2000/svg" width="320" height="320" viewBox="0 0 320 320">
      <defs>
        <linearGradient id="bg" x1="0" x2="1" y1="0" y2="1">
          <stop offset="0%" stop-color="${bgA}"/>
          <stop offset="100%" stop-color="${bgB}"/>
        </linearGradient>
        <linearGradient id="shirt" x1="0" x2="0" y1="0" y2="1">
          <stop offset="0%" stop-color="${shirt}"/>
          <stop offset="100%" stop-color="#111319"/>
        </linearGradient>
      </defs>
      <rect width="320" height="320" rx="52" fill="url(#bg)"/>
      <circle cx="258" cy="70" r="58" fill="rgba(255,255,255,0.22)"/>
      <circle cx="76" cy="262" r="104" fill="rgba(255,255,255,0.12)"/>
      <rect x="64" y="204" width="192" height="116" rx="58" fill="url(#shirt)"/>
      <rect x="113" y="160" width="94" height="58" rx="24" fill="${skin}"/>
      <circle cx="160" cy="119" r="62" fill="${skin}"/>
      <path d="M97 122c4-48 32-76 68-76 37 0 64 25 67 74-26-20-53-29-79-26-22 2-39 10-56 28z" fill="${hair}"/>
      <path d="M104 120c18-30 42-43 72-39 20 3 38 12 55 29-8-37-35-61-68-61-35 0-61 27-59 71z" fill="rgba(255,255,255,0.08)"/>
      <circle cx="139" cy="122" r="4" fill="#38251c"/>
      <circle cx="181" cy="122" r="4" fill="#38251c"/>
      <path d="M142 148c9 8 27 8 36 0" fill="none" stroke="#a66b58" stroke-width="5" stroke-linecap="round"/>
      <path d="M76 304h168" stroke="rgba(255,255,255,0.22)" stroke-width="10" stroke-linecap="round"/>
    </svg>
  `;
  return `data:image/svg+xml;charset=UTF-8,${encodeURIComponent(svg)}`;
}

function createGymAvatar(options) {
  const { bgA = "#26323e", bgB = "#7b91a8", accent = "#f28c28" } = options;
  const svg = `
    <svg xmlns="http://www.w3.org/2000/svg" width="320" height="320" viewBox="0 0 320 320">
      <defs>
        <linearGradient id="bg" x1="0" x2="1" y1="0" y2="1">
          <stop offset="0%" stop-color="${bgA}"/>
          <stop offset="100%" stop-color="${bgB}"/>
        </linearGradient>
        <linearGradient id="floor" x1="0" x2="1" y1="0" y2="1">
          <stop offset="0%" stop-color="#e7ded0"/>
          <stop offset="100%" stop-color="#a98860"/>
        </linearGradient>
      </defs>
      <rect width="320" height="320" rx="52" fill="url(#bg)"/>
      <rect x="0" y="202" width="320" height="118" fill="url(#floor)" opacity="0.92"/>
      <rect x="28" y="42" width="264" height="126" rx="24" fill="rgba(225,239,246,0.78)"/>
      <path d="M116 42v126M204 42v126M28 104h264" stroke="rgba(255,255,255,0.72)" stroke-width="7"/>
      <rect x="54" y="154" width="72" height="94" rx="15" fill="#2d343d"/>
      <rect x="70" y="170" width="40" height="10" rx="5" fill="${accent}"/>
      <rect x="76" y="192" width="10" height="42" rx="5" fill="#cfd6dc"/>
      <rect x="96" y="184" width="10" height="50" rx="5" fill="#cfd6dc"/>
      <rect x="150" y="206" width="108" height="16" rx="8" fill="#30343b"/>
      <circle cx="162" cy="236" r="18" fill="#30343b"/>
      <circle cx="246" cy="236" r="18" fill="#30343b"/>
      <rect x="218" y="126" width="54" height="96" rx="18" fill="rgba(37,44,52,0.86)"/>
      <rect x="230" y="144" width="30" height="54" rx="10" fill="#aab6bf"/>
    </svg>
  `;
  return `data:image/svg+xml;charset=UTF-8,${encodeURIComponent(svg)}`;
}

const DEMO_PROFILE_PATCHES = {
  "gym-demo-a": {
    name: "模拟健身房 A · 万象燃炼馆",
    avatar: "万",
    avatarImage: demoAsset("gym-a-avatar.jpg"),
    coverImage: demoAsset("gym-a.jpg"),
    bio: "模拟门店，位于厦门万象城商圈，用于测试真实场馆照片、定价、预约、评分和主页展示。",
    shortDesc: "万象城商圈器械馆，支持月卡、次卡和团课测试。",
    price: "¥169/月起",
    tags: ["模拟场馆", "力量区", "团课"],
    hours: "06:00 - 24:00",
    contactName: "测试店长 林楠",
    pricingPlans: [
      { title: "月卡", detail: "器械区 + 更衣淋浴", price: "¥169/月" },
      { title: "次卡", detail: "12 次 90 天有效", price: "¥299/12次" },
      { title: "团课卡", detail: "搏击 / 单车 / HIIT", price: "¥399/16节" }
    ]
  },
  "gym-demo-b": {
    name: "模拟健身房 B · 轻氧塑能馆",
    avatar: "氧",
    avatarImage: demoAsset("gym-b-avatar.jpg"),
    coverImage: demoAsset("gym-b.jpg"),
    bio: "模拟精品训练馆，主打轻氧有氧和恢复类课程，适合测试价格展示和课程预约。",
    shortDesc: "精品有氧空间，适合恢复训练和轻团课测试。",
    price: "¥138/月起",
    tags: ["模拟场馆", "精品馆", "恢复"],
    hours: "07:00 - 23:00",
    contactName: "测试店长 苏越",
    pricingPlans: [
      { title: "轻氧月卡", detail: "跑步机 + 骑行区", price: "¥138/月" },
      { title: "午间卡", detail: "工作日 11:00-16:00", price: "¥99/月" },
      { title: "恢复课包", detail: "拉伸恢复 8 节", price: "¥699/8节" }
    ]
  },
  "coach-demo-a": {
    name: "模拟教练 A · 林燃",
    avatar: "林",
    avatarImage: demoAsset("coach-a-avatar.jpg"),
    coverImage: demoAsset("coach-a.jpg"),
    bio: "模拟私教，擅长力量提升和减脂塑形，用于测试真实头像、课时定价、预约和私信。",
    shortDesc: "力量提升、减脂塑形，适合测试私教预约。",
    price: "¥299/小时",
    tags: ["模拟教练", "力量提升", "减脂塑形"],
    years: "8",
    certifications: ["NASM", "ACE", "CBBA"],
    pricingPlans: [
      { title: "私教 1v1", detail: "动作纠正 + 饮食建议", price: "¥299/小时" },
      { title: "12 节进阶包", detail: "适合 6 周增肌减脂周期", price: "¥3180/12节" },
      { title: "双人训练", detail: "两人拼课", price: "¥420/小时" }
    ]
  },
  "coach-demo-b": {
    name: "模拟教练 B · 周芮",
    avatar: "周",
    avatarImage: demoAsset("coach-b-avatar.jpg"),
    coverImage: demoAsset("coach-b.jpg"),
    bio: "模拟女教练，主打体态改善和普拉提恢复，方便测试女性教练主页、评分和动态流。",
    shortDesc: "体态改善、核心激活，适合恢复和普拉提测试。",
    price: "¥268/小时",
    tags: ["模拟教练", "普拉提", "体态改善"],
    years: "5",
    certifications: ["Balanced Body", "ACE"],
    pricingPlans: [
      { title: "普拉提 1v1", detail: "核心激活 + 体态改善", price: "¥268/小时" },
      { title: "恢复课包", detail: "8 节核心恢复课程", price: "¥1880/8节" },
      { title: "双人塑形课", detail: "适合闺蜜或情侣", price: "¥360/小时" }
    ]
  }
};

const DEMO_POST_MEDIA = {
  "gym-demo-a": [
    { type: "image", url: demoAsset("gym-a.jpg"), name: "demo-gym-a.jpg" },
    { type: "image", url: demoAsset("gym-d.jpg"), name: "demo-gym-a-free-weight.jpg" }
  ],
  "gym-demo-b": [{ type: "image", url: demoAsset("gym-b.jpg"), name: "demo-gym-b.jpg" }],
  "gym-demo-c": [{ type: "image", url: demoAsset("gym-c.jpg"), name: "demo-gym-c.jpg" }],
  "gym-demo-d": [{ type: "image", url: demoAsset("gym-d.jpg"), name: "demo-gym-d.jpg" }],
  "coach-demo-a": [{ type: "image", url: demoAsset("coach-a.jpg"), name: "demo-coach-a.jpg" }],
  "coach-demo-b": [{ type: "image", url: demoAsset("coach-b.jpg"), name: "demo-coach-b.jpg" }],
  "coach-demo-c": [{ type: "image", url: demoAsset("coach-c.jpg"), name: "demo-coach-c.jpg" }],
  "coach-demo-d": [{ type: "image", url: demoAsset("coach-d.jpg"), name: "demo-coach-d.jpg" }]
};

function normalizeDemoPostMedia(profile) {
  const demoMedia = DEMO_POST_MEDIA[profile?.id];
  if (!demoMedia || !Array.isArray(profile.posts)) return profile;
  return {
    ...profile,
    posts: profile.posts.map((post, index) => {
      if (!post?.id) return post;
      const shouldShowMedia =
        isMediaPost(post) ||
        profile.id !== "gym-demo-a" ||
        /器械|设备|场馆|夜训|力量|塑形|训练|档期|课程/.test(`${post.content || ""}${post.meta || ""}`) ||
        index > 0;
      if (!shouldShowMedia) return post;
      return {
        ...post,
        media: demoMedia.map((item) => ({ ...item }))
      };
    })
  };
}

function applyDemoProfilePatch(profile) {
  if (!profile) return profile;
  const patch = DEMO_PROFILE_PATCHES[profile.id];
  if (!patch) return normalizeDemoPostMedia(profile);
  return normalizeDemoPostMedia({
    ...profile,
    ...patch
  });
}

function isGeneratedInlineAvatar(url) {
  if (typeof url !== "string" || !url.startsWith("data:image/svg")) return false;
  try {
    const decoded = decodeURIComponent(url);
    return decoded.includes('viewBox="0 0 320 320"') && (decoded.includes("linearGradient") || decoded.includes("rgba("));
  } catch (_error) {
    return false;
  }
}

function normalizeDefaultAvatar(profile) {
  if (!profile || String(profile.id || "").includes("demo")) return profile;
  if (!isGeneratedInlineAvatar(profile.avatarImage)) return profile;
  return {
    ...profile,
    avatarImage: createDefaultAvatar(profile.role, profile.name)
  };
}

function enhanceProfiles(profiles = []) {
  return profiles.map((profile) => normalizeDefaultAvatar(applyDemoProfilePatch(profile)));
}

function createShopArtwork({
  sticker = "FIT",
  title = "训练好物",
  subtitle = "FITHUB SELECT",
  bgA = "#fff1df",
  bgB = "#f2b067",
  accent = "#f28c28",
  panel = "#1e2530"
}) {
  const svg = `
    <svg xmlns="http://www.w3.org/2000/svg" width="640" height="480" viewBox="0 0 640 480">
      <defs>
        <linearGradient id="bg" x1="0" x2="1" y1="0" y2="1">
          <stop offset="0%" stop-color="${bgA}"/>
          <stop offset="100%" stop-color="${bgB}"/>
        </linearGradient>
        <linearGradient id="panel" x1="0" x2="1" y1="0" y2="1">
          <stop offset="0%" stop-color="${panel}"/>
          <stop offset="100%" stop-color="#0f141c"/>
        </linearGradient>
      </defs>
      <rect width="640" height="480" rx="40" fill="url(#bg)"/>
      <circle cx="548" cy="92" r="62" fill="rgba(255,255,255,0.16)"/>
      <circle cx="96" cy="404" r="88" fill="rgba(255,255,255,0.10)"/>
      <rect x="54" y="54" width="532" height="372" rx="34" fill="url(#panel)" opacity="0.92"/>
      <rect x="88" y="92" width="122" height="44" rx="22" fill="${accent}"/>
      <text x="149" y="121" text-anchor="middle" font-family="Arial, sans-serif" font-size="22" font-weight="700" fill="#fff">${sticker}</text>
      <rect x="88" y="188" width="176" height="30" rx="15" fill="rgba(255,255,255,0.12)"/>
      <rect x="88" y="236" width="236" height="22" rx="11" fill="rgba(255,255,255,0.12)"/>
      <rect x="88" y="272" width="202" height="22" rx="11" fill="rgba(255,255,255,0.08)"/>
      <circle cx="462" cy="218" r="74" fill="rgba(242,140,40,0.18)"/>
      <circle cx="462" cy="218" r="50" fill="rgba(255,255,255,0.16)"/>
      <path d="M418 218h88" stroke="${accent}" stroke-width="12" stroke-linecap="round"/>
      <circle cx="436" cy="218" r="18" fill="${accent}"/>
      <circle cx="488" cy="218" r="18" fill="${accent}"/>
      <text x="88" y="356" font-family="Arial, sans-serif" font-size="38" font-weight="700" fill="#fff">${title}</text>
      <text x="88" y="392" font-family="Arial, sans-serif" font-size="18" letter-spacing="2" fill="rgba(255,255,255,0.68)">${subtitle}</text>
    </svg>
  `;
  return `data:image/svg+xml;charset=UTF-8,${encodeURIComponent(svg)}`;
}

const SHOP_CATEGORY_OPTIONS = [
  { id: "all", label: "全部" },
  { id: "strength", label: "力量器械" },
  { id: "recovery", label: "恢复放松" },
  { id: "wearable", label: "智能穿戴" },
  { id: "nutrition", label: "补给营养" },
  { id: "merch", label: "门店周边" }
];

const SHOP_PRODUCTS = [
  {
    id: "shop-dumbbell-pro",
    category: "strength",
    title: "燃炼六角哑铃 10kg",
    subtitle: "包胶静音，适合家庭训练与门店补货",
    price: "¥189",
    originalPrice: "¥229",
    badge: "同城热卖",
    sellerProfileId: "gym-demo-a",
    sellerType: "gym",
    city: "厦门 · 思明区",
    rating: "4.9",
    sold: "已售 83",
    stock: "剩余 18 件",
    tags: ["力量训练", "门店自提", "团课同款"],
    image: createShopArtwork({
      sticker: "10KG",
      title: "六角哑铃",
      subtitle: "DUMBBELL SET",
      bgA: "#fff4e5",
      bgB: "#e8b175",
      accent: "#f28c28"
    })
  },
  {
    id: "shop-band-set",
    category: "strength",
    title: "弹力带训练组合",
    subtitle: "教练推荐的居家激活与热身套装",
    price: "¥128",
    originalPrice: "¥159",
    badge: "教练推荐",
    sellerProfileId: "coach-demo-a",
    sellerType: "coach",
    city: "厦门 · 思明区",
    rating: "4.8",
    sold: "已售 47",
    stock: "剩余 26 件",
    tags: ["动作激活", "热身", "新手友好"],
    image: createShopArtwork({
      sticker: "BAND",
      title: "弹力带组合",
      subtitle: "ACTIVATION KIT",
      bgA: "#fff1e8",
      bgB: "#d79a71",
      accent: "#f28c28"
    })
  },
  {
    id: "shop-foam-roller",
    category: "recovery",
    title: "深层筋膜泡沫轴",
    subtitle: "适合拉伸、恢复与训练后放松",
    price: "¥99",
    originalPrice: "¥129",
    badge: "恢复专区",
    sellerProfileId: "gym-demo-b",
    sellerType: "gym",
    city: "厦门 · 湖里区",
    rating: "4.7",
    sold: "已售 61",
    stock: "剩余 35 件",
    tags: ["恢复放松", "核心训练", "团课常备"],
    image: createShopArtwork({
      sticker: "ROLL",
      title: "筋膜泡沫轴",
      subtitle: "RECOVERY",
      bgA: "#f7f1ff",
      bgB: "#c8b7ff",
      accent: "#8b6bff"
    })
  },
  {
    id: "shop-massage-gun",
    category: "recovery",
    title: "便携筋膜枪",
    subtitle: "训练后 10 分钟快速放松与激活",
    price: "¥299",
    originalPrice: "¥369",
    badge: "人气恢复",
    sellerProfileId: "coach-demo-b",
    sellerType: "coach",
    city: "厦门 · 湖里区",
    rating: "4.9",
    sold: "已售 29",
    stock: "剩余 12 件",
    tags: ["恢复", "体态改善", "便携"],
    image: createShopArtwork({
      sticker: "GUN",
      title: "便携筋膜枪",
      subtitle: "RECOVER FAST",
      bgA: "#f7f3ed",
      bgB: "#d0b494",
      accent: "#7f5c41"
    })
  },
  {
    id: "shop-smart-scale",
    category: "wearable",
    title: "智能体脂秤",
    subtitle: "支持体重、BMI 与体脂同步记录",
    price: "¥249",
    originalPrice: "¥299",
    badge: "数据追踪",
    sellerProfileId: "gym-demo-c",
    sellerType: "gym",
    city: "厦门 · 海沧区",
    rating: "4.8",
    sold: "已售 42",
    stock: "剩余 21 件",
    tags: ["体脂监测", "健康管理", "训练伴侣"],
    image: createShopArtwork({
      sticker: "BODY",
      title: "智能体脂秤",
      subtitle: "SMART SCALE",
      bgA: "#edf7ff",
      bgB: "#9bc7f5",
      accent: "#4f8edb"
    })
  },
  {
    id: "shop-watch-strap",
    category: "wearable",
    title: "训练表带快拆款",
    subtitle: "适配运动手表与高频训练场景",
    price: "¥79",
    originalPrice: "¥99",
    badge: "配件热卖",
    sellerProfileId: "coach-demo-d",
    sellerType: "coach",
    city: "厦门 · 集美区",
    rating: "4.6",
    sold: "已售 57",
    stock: "剩余 33 件",
    tags: ["穿戴配件", "透气", "耐汗"],
    image: createShopArtwork({
      sticker: "WATCH",
      title: "训练表带",
      subtitle: "SPORT STRAP",
      bgA: "#f0f5ff",
      bgB: "#94aee9",
      accent: "#5670d6"
    })
  },
  {
    id: "shop-whey-protein",
    category: "nutrition",
    title: "分离乳清蛋白 900g",
    subtitle: "适合减脂增肌周期的训练补给",
    price: "¥268",
    originalPrice: "¥328",
    badge: "平台精选",
    sellerProfileId: "gym-demo-d",
    sellerType: "gym",
    city: "厦门 · 集美区",
    rating: "4.9",
    sold: "已售 103",
    stock: "剩余 16 件",
    tags: ["训练补给", "高蛋白", "平台精选"],
    image: createShopArtwork({
      sticker: "PRO",
      title: "乳清蛋白",
      subtitle: "WHEY PROTEIN",
      bgA: "#fff6e9",
      bgB: "#f1c06b",
      accent: "#f28c28"
    })
  },
  {
    id: "shop-shaker-bottle",
    category: "merch",
    title: "FitHub 联名摇摇杯",
    subtitle: "通勤训练两用，适合教练与会员随身携带",
    price: "¥59",
    originalPrice: "¥79",
    badge: "联名周边",
    sellerProfileId: "gym-demo-a",
    sellerType: "gym",
    city: "厦门 · 思明区",
    rating: "4.8",
    sold: "已售 90",
    stock: "剩余 40 件",
    tags: ["门店周边", "联名", "轻量"],
    image: createShopArtwork({
      sticker: "SHAKE",
      title: "联名摇摇杯",
      subtitle: "FITHUB MERCH",
      bgA: "#fff0ec",
      bgB: "#ef9d8f",
      accent: "#dd6b50"
    })
  },
  {
    id: "shop-grip-gloves",
    category: "merch",
    title: "力量训练防滑手套",
    subtitle: "深蹲硬拉与推举都更稳的基础装备",
    price: "¥88",
    originalPrice: "¥108",
    badge: "门店同款",
    sellerProfileId: "gym-demo-c",
    sellerType: "gym",
    city: "厦门 · 海沧区",
    rating: "4.7",
    sold: "已售 38",
    stock: "剩余 19 件",
    tags: ["防滑", "力量训练", "高频复购"],
    image: createShopArtwork({
      sticker: "GRIP",
      title: "训练手套",
      subtitle: "LIFT GLOVES",
      bgA: "#f5f0ff",
      bgB: "#c6b4f4",
      accent: "#8d68db"
    })
  }
];

function createSupplementalDemoProfiles() {
  return enhanceProfiles([
    {
      id: "gym-demo-c",
      role: "gym",
      name: "模拟健身房 C · Skyline Strength",
      handle: "@demo.gym.c",
      avatar: "天",
      avatarImage: demoAsset("gym-c-avatar.jpg"),
      coverImage: demoAsset("gym-c.jpg"),
      city: "厦门",
      locationLabel: "厦门 · 思明区 · 环岛路",
      lat: 24.4576,
      lng: 118.1103,
      bio: "模拟高景观力量馆，方便测试真实场馆图、主页头图、预约链路和价格展示。",
      shortDesc: "海景力量训练馆，适合展示精品月卡和私教区。",
      price: "¥199/月起",
      tags: ["模拟场馆", "景观馆", "力量"],
      hours: "06:30 - 23:30",
      contactName: "测试店长 韩玥",
      phone: "13800000003",
      pricingPlans: [
        { title: "精品月卡", detail: "含自由训练区", price: "¥199/月" },
        { title: "季卡", detail: "90 天畅练", price: "¥499/季" },
        { title: "私教区使用包", detail: "适合预约私教", price: "¥159/次" }
      ],
      followers: 2140,
      following: 26,
      ratingAvg: 4.8,
      ratingCount: 144,
      listed: true,
      posts: [
        {
          time: "1 小时前",
          content: "海景跑步区今晚延长到 23:30，适合测试夜间训练场景。",
          meta: "模拟动态 · 夜场开放",
          media: [
            {
              type: "image",
              url: demoAsset("gym-c.jpg"),
              name: "demo-gym-c.jpg"
            }
          ]
        }
      ],
      reviews: [
        { author: "模拟用户 A", score: 5, text: "视野很好，适合拿来展示精品馆体验。", time: "昨天" }
      ]
    },
    {
      id: "gym-demo-d",
      role: "gym",
      name: "模拟健身房 D · 城市力量馆",
      handle: "@demo.gym.d",
      avatar: "城",
      avatarImage: demoAsset("gym-d-avatar.jpg"),
      coverImage: demoAsset("gym-d.jpg"),
      city: "厦门",
      locationLabel: "厦门 · 湖里区 · SM 商圈",
      lat: 24.5088,
      lng: 118.1295,
      bio: "模拟综合器械馆，器械和自由重量区完整，适合测试主页定价、预约和评分模块。",
      shortDesc: "器械区完整，适合测试多种会员卡方案。",
      price: "¥149/月起",
      tags: ["模拟场馆", "器械区", "自由重量"],
      hours: "24h 营业",
      contactName: "测试店长 程序",
      phone: "13800000004",
      pricingPlans: [
        { title: "月卡", detail: "24h 进店训练", price: "¥149/月" },
        { title: "力量卡", detail: "自由重量区优先", price: "¥239/月" },
        { title: "新人体验卡", detail: "7 天不限次", price: "¥59/周" }
      ],
      followers: 1874,
      following: 31,
      ratingAvg: 4.6,
      ratingCount: 201,
      listed: true,
      posts: [
        {
          time: "今天",
          content: "自由重量区新调了灯光和动线，方便测试真实门店展示效果。",
          meta: "模拟动态 · 场馆升级",
          media: [
            {
              type: "image",
              url: demoAsset("gym-d.jpg"),
              name: "demo-gym-d.jpg"
            }
          ]
        }
      ],
      reviews: [
        { author: "模拟用户 B", score: 4, text: "器械全，适合演示会员定价和主页。", time: "2 天前" }
      ]
    },
    {
      id: "coach-demo-c",
      role: "coach",
      name: "模拟教练 C · 陈拓",
      handle: "@demo.coach.c",
      avatar: "陈",
      avatarImage: demoAsset("coach-c-avatar.jpg"),
      coverImage: demoAsset("coach-c.jpg"),
      city: "厦门",
      locationLabel: "厦门 · 湖里区 · 五缘湾",
      lat: 24.5223,
      lng: 118.1563,
      bio: "模拟男教练，用于测试增肌、力量和大课包的价格展示与预约互动。",
      shortDesc: "增肌力量、训练计划制定，适合进阶课包测试。",
      price: "¥328/小时",
      tags: ["模拟教练", "增肌", "力量训练"],
      years: "7",
      certifications: ["NSCA", "CBBA"],
      pricingPlans: [
        { title: "进阶私教", detail: "增肌 + 力量计划", price: "¥328/小时" },
        { title: "16 节课包", detail: "适合系统周期训练", price: "¥4380/16节" },
        { title: "训练营小班", detail: "4 人内小班训练", price: "¥129/人/节" }
      ],
      followers: 1728,
      following: 39,
      ratingAvg: 4.9,
      ratingCount: 126,
      listed: true,
      posts: [
        {
          time: "45 分钟前",
          content: "本周新开了一组 4 人力量训练营，方便测试多种定价模式。",
          meta: "模拟动态 · 训练营上新",
          media: [{ type: "image", url: demoAsset("coach-c.jpg"), name: "demo-coach-c.jpg" }]
        }
      ],
      reviews: [
        { author: "模拟用户 A", score: 5, text: "训练计划很清晰，适合演示教练主页。", time: "3 天前" }
      ]
    },
    {
      id: "coach-demo-d",
      role: "coach",
      name: "模拟教练 D · Mia 沈",
      handle: "@demo.coach.d",
      avatar: "M",
      avatarImage: demoAsset("coach-d-avatar.jpg"),
      coverImage: demoAsset("coach-d.jpg"),
      city: "厦门",
      locationLabel: "厦门 · 思明区 · 明发商业广场",
      lat: 24.4714,
      lng: 118.1041,
      bio: "模拟女教练，主打女性塑形和功能性训练，方便测试头像、价格和私信功能。",
      shortDesc: "女性塑形、功能训练，适合晚间档期预约测试。",
      price: "¥248/小时",
      tags: ["模拟教练", "女性塑形", "功能训练"],
      years: "4",
      certifications: ["ACE", "FMS"],
      pricingPlans: [
        { title: "塑形 1v1", detail: "女性塑形 + 体态调整", price: "¥248/小时" },
        { title: "夜间课包", detail: "下班后专属时段", price: "¥2580/12节" },
        { title: "双人塑形课", detail: "适合好友一起练", price: "¥340/小时" }
      ],
      followers: 1540,
      following: 54,
      ratingAvg: 4.8,
      ratingCount: 118,
      listed: true,
      posts: [
        {
          time: "2 小时前",
          content: "新增了 20:30 的晚间塑形档期，方便测试即时预约和私信咨询。",
          meta: "模拟动态 · 晚间时段",
          media: [{ type: "image", url: demoAsset("coach-d.jpg"), name: "demo-coach-d.jpg" }]
        }
      ],
      reviews: [
        { author: "模拟用户 B", score: 5, text: "沟通很舒服，适合测试女教练主页体验。", time: "昨天" }
      ]
    }
  ]);
}

function getProfileCoverImage(profile) {
  return profile?.coverImage || profile?.avatarImage || "";
}

function optimizeRemoteImageUrl(url, kind = "avatar") {
  if (!url || typeof url !== "string" || !/^https?:\/\//.test(url)) return url;

  try {
    const remoteUrl = new URL(url);
    if (remoteUrl.hostname !== "images.pexels.com") return url;
    const localPexelsMap = {
      "6046979": "gym-a",
      "35215412": "gym-b",
      "28455437": "coach-a",
      "14055666": "coach-b",
      "29149075": "gym-c",
      "4716817": "gym-d",
      "11327778": "coach-c",
      "20418608": "coach-d"
    };
    const matchedId = Object.keys(localPexelsMap).find((photoId) => remoteUrl.pathname.includes(photoId));
    if (matchedId) {
      const assetName = localPexelsMap[matchedId];
      return demoAsset(kind === "avatar" ? `${assetName}-avatar.jpg` : `${assetName}.jpg`);
    }
    return kind === "avatar" ? createDefaultAvatar("enthusiast", "") : createDemoImage("FitHub 训练瞬间", "#f4efe7", "#f28c28");

  } catch (_error) {
    return url;
  }
}

function createNeutralAvatar(role = "enthusiast") {
  const isGym = role === "gym";
  const badge = isGym
    ? `<path d="M105 170h110v74H105z" fill="#eef4f8"/><path d="M126 170v74M160 170v74M194 170v74M105 204h110" stroke="#c7d3dc" stroke-width="8"/>`
    : `<circle cx="160" cy="126" r="48" fill="#f4f7f9"/><path d="M78 286c13-64 46-97 82-97s69 33 82 97" fill="#f4f7f9"/>`;
  const svg = `
    <svg xmlns="http://www.w3.org/2000/svg" width="320" height="320" viewBox="0 0 320 320">
      <defs>
        <linearGradient id="bg" x1="0" x2="1" y1="0" y2="1">
          <stop offset="0%" stop-color="#eef3f7"/>
          <stop offset="100%" stop-color="#cbd8e3"/>
        </linearGradient>
        <filter id="shadow" x="-20%" y="-20%" width="140%" height="140%">
          <feDropShadow dx="0" dy="12" stdDeviation="14" flood-color="#7d8b98" flood-opacity="0.18"/>
        </filter>
      </defs>
      <rect width="320" height="320" rx="62" fill="url(#bg)"/>
      <circle cx="244" cy="74" r="58" fill="rgba(255,255,255,0.46)"/>
      <circle cx="88" cy="256" r="110" fill="rgba(255,255,255,0.24)"/>
      <g filter="url(#shadow)">${badge}</g>
      <path d="M96 286h128" stroke="rgba(117,132,146,0.32)" stroke-width="10" stroke-linecap="round"/>
    </svg>
  `;
  return `data:image/svg+xml;charset=UTF-8,${encodeURIComponent(svg)}`;
}

function hydrateAsyncImages(root = document) {
  root.querySelectorAll(".image-shell").forEach((shell) => {
    const image = shell.querySelector("img");
    if (!image || shell.dataset.imageHydrated === "1" || shell.dataset.imageObserved === "1") return;
    if (image.complete || root !== appView) {
      bindImageShell(shell);
      return;
    }
    const observer = getImageHydrationObserver();
    if (!observer) {
      bindImageShell(shell);
      return;
    }
    shell.dataset.imageObserved = "1";
    observer.observe(shell);
  });
}

function createDefaultAvatar(role, name) {
  return createNeutralAvatar(role || "enthusiast");
}

const imageShellStateQueue = new Map();
let imageShellStateFrame = 0;
let imageHydrationObserver = null;

function flushImageShellStates() {
  imageShellStateFrame = 0;
  imageShellStateQueue.forEach((status, shell) => {
    shell.classList.remove("is-loaded", "is-failed");
    if (status === "loaded") shell.classList.add("is-loaded");
    if (status === "failed") shell.classList.add("is-failed");
  });
  imageShellStateQueue.clear();
}

function scheduleImageShellState(shell, status) {
  imageShellStateQueue.set(shell, status);
  if (imageShellStateFrame) return;
  imageShellStateFrame = window.requestAnimationFrame
    ? window.requestAnimationFrame(flushImageShellStates)
    : window.setTimeout(flushImageShellStates, 16);
}

function bindImageShell(shell) {
  const image = shell.querySelector("img");
  if (!image || shell.dataset.imageHydrated === "1") return;
  shell.dataset.imageHydrated = "1";

  const markLoaded = () => {
    scheduleImageShellState(shell, "loaded");
  };

  const markFailed = () => {
    scheduleImageShellState(shell, "failed");
  };

  if (image.complete) {
    if (image.naturalWidth > 0) {
      markLoaded();
    } else {
      markFailed();
    }
    return;
  }

  image.addEventListener("load", markLoaded, { once: true });
  image.addEventListener("error", markFailed, { once: true });
}

function getImageHydrationObserver() {
  if (!("IntersectionObserver" in window)) return null;
  if (imageHydrationObserver) return imageHydrationObserver;
  imageHydrationObserver = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (!entry.isIntersecting && entry.intersectionRatio <= 0) return;
        imageHydrationObserver.unobserve(entry.target);
        bindImageShell(entry.target);
      });
    },
    { rootMargin: "520px 0px", threshold: 0.01 }
  );
  return imageHydrationObserver;
}

function createInitialProfiles() {
  return [
    {
      id: "enthusiast-demo-a",
      role: "enthusiast",
      name: "模拟用户 A",
      handle: "@demo.user.a",
      avatar: "A",
      avatarImage: createPortraitAvatar({ skin: "#f6d1b5", hair: "#6b4736", shirt: "#f28c28", bgA: "#f6dfc7", bgB: "#d6a174" }),
      city: "厦门",
      locationLabel: "厦门 · 思明区",
      lat: 24.4812,
      lng: 118.0911,
      bio: "模拟测试用户，主要用于测试关注、预约、评分和动态发布。",
      shortDesc: "规律训练 10 个月，方便测试健身圈互动。",
      price: "",
      tags: ["模拟用户", "减脂", "打卡"],
      level: "规律训练",
      goal: "减脂 5kg，维持一周四练",
      followers: 0,
      following: 0,
      ratingAvg: 0,
      ratingCount: 0,
      listed: false,
      posts: [],
      checkins: [],
      reviews: []
    },
    {
      id: "enthusiast-demo-b",
      role: "enthusiast",
      name: "模拟用户 B",
      handle: "@demo.user.b",
      avatar: "B",
      avatarImage: createPortraitAvatar({ skin: "#f1c7ad", hair: "#50372b", shirt: "#4f7ea1", bgA: "#f0d8c5", bgB: "#d2a183" }),
      city: "厦门",
      locationLabel: "厦门 · 湖里区",
      lat: 24.5008,
      lng: 118.1172,
      bio: "模拟测试用户，主要用来测试课程预约、评价和关注功能。",
      shortDesc: "训练新手，主要测试预约、评分和定位模块。",
      price: "",
      tags: ["模拟用户", "新手入门", "塑形"],
      level: "新手入门",
      goal: "每周三练，改善体态",
      followers: 0,
      following: 0,
      ratingAvg: 0,
      ratingCount: 0,
      listed: false,
      posts: [],
      checkins: [],
      reviews: []
    },
    {
      id: "gym-demo-a",
      role: "gym",
      name: "模拟健身房 A",
      handle: "@demo.gym.a",
      avatar: "馆",
      avatarImage: createGymAvatar({ bgA: "#1f2a34", bgB: "#748ca2", accent: "#f28c28" }),
      city: "厦门",
      locationLabel: "厦门 · 思明区",
      lat: 24.4828,
      lng: 118.0958,
      bio: "模拟健身房 A 用于测试场馆主页、定价、定位、预约和评分链路。",
      shortDesc: "24h 营业，团课丰富，适合测试预约功能。",
      price: "¥119/月起",
      tags: ["模拟场馆", "24h", "团课"],
      hours: "24h 营业",
      contactName: "测试店长 A",
      phone: "13800000001",
      pricingPlans: [
        { title: "月卡", detail: "不限次进店", price: "¥119/月" },
        { title: "次卡", detail: "10 次内 60 天有效", price: "¥199/10次" },
        { title: "团课包", detail: "燃脂 / 力量 / 单车", price: "¥299/12节" }
      ],
      followers: 2418,
      following: 36,
      ratingAvg: 4.8,
      ratingCount: 328,
      listed: true,
      posts: [
        { time: "1 小时前", content: "今晚 19:30 燃脂单车还剩 8 个名额。", meta: "课程提醒" },
        {
          time: "今天",
          content: "模拟健身房 A 新到一批力量器械，方便测试场馆动态展示。",
          meta: "模拟动态 · 设备更新",
          media: [
            {
              type: "image",
              url: createDemoImage("器械上新", "#f19a3e", "#2f8c88"),
              name: "demo-gym-a-1.jpg"
            },
            {
              type: "image",
              url: createDemoImage("团课教室", "#3a8fd1", "#6cc3a0"),
              name: "demo-gym-a-2.jpg"
            }
          ]
        }
      ],
      reviews: [
        { author: "模拟用户 A", score: 5, text: "器械很新，晚间也不拥挤，适合测试预约。", time: "2 天前" },
        { author: "Mia 教练", score: 4, text: "团课教室空间不错，动线清晰。", time: "5 天前" }
      ]
    },
    {
      id: "gym-demo-b",
      role: "gym",
      name: "模拟健身房 B",
      handle: "@demo.gym.b",
      avatar: "泳",
      avatarImage: createGymAvatar({ bgA: "#214d64", bgB: "#76aeca", accent: "#59d4ff" }),
      city: "厦门",
      locationLabel: "厦门 · 湖里区",
      lat: 24.5064,
      lng: 118.1268,
      bio: "模拟健身房 B 用于测试泳池馆场景、价格展示和恢复课程预约。",
      shortDesc: "恒温泳池，适合测试恢复训练和课程包。",
      price: "¥138/月起",
      tags: ["模拟场馆", "泳池", "康复"],
      hours: "06:00 - 23:00",
      contactName: "测试店长 B",
      phone: "13800000002",
      pricingPlans: [
        { title: "游泳月卡", detail: "泳池 + 更衣淋浴", price: "¥138/月" },
        { title: "家庭卡", detail: "2 大 1 小共享", price: "¥368/月" },
        { title: "康复课程包", detail: "恢复训练 8 节", price: "¥699/8节" }
      ],
      followers: 1630,
      following: 18,
      ratingAvg: 4.7,
      ratingCount: 216,
      listed: true,
      posts: [
        { time: "3 小时前", content: "模拟健身房 B 的周末亲子游泳课已开放预约。", meta: "模拟动态 · 课程更新" }
      ],
      reviews: [
        { author: "模拟用户 B", score: 5, text: "泳池环境很干净，适合测试家庭卡展示。", time: "昨天" }
      ]
    },
    {
      id: "coach-demo-a",
      role: "coach",
      name: "模拟教练 A",
      handle: "@demo.coach.a",
      avatar: "林",
      avatarImage: createPortraitAvatar({ skin: "#efc3a4", hair: "#281d17", shirt: "#17181d", bgA: "#d9e0ea", bgB: "#8b98ad" }),
      city: "厦门",
      locationLabel: "厦门 · 思明区",
      lat: 24.4805,
      lng: 118.0874,
      bio: "模拟教练 A 主要用于测试私教定价、档期、评价和主页动态。",
      shortDesc: "塑形增肌、燃脂减脂，适合测试私教预约。",
      price: "¥260/小时",
      tags: ["模拟教练", "减脂塑形", "力量提升"],
      years: "6",
      certifications: ["NASM", "ACE", "CBBA"],
      pricingPlans: [
        { title: "私教 1v1", detail: "动作纠正 + 饮食建议", price: "¥260/小时" },
        { title: "12 节课包", detail: "适合减脂塑形周期", price: "¥2880/12节" },
        { title: "双人训练", detail: "两人拼课", price: "¥380/小时" }
      ],
      followers: 1890,
      following: 42,
      ratingAvg: 4.9,
      ratingCount: 274,
      listed: true,
      posts: [
        { time: "30 分钟前", content: "模拟教练 A 今晚开放两个私教档期，方便测试即时预约。", meta: "模拟动态 · 即时空闲" },
        {
          time: "昨天",
          content: "整理了一份模拟学员常见动作错误清单。",
          meta: "模拟动态 · 训练干货",
          media: [
            {
              type: "image",
              url: createDemoImage("动作纠正", "#293b72", "#6a82fb"),
              name: "demo-coach-a.jpg"
            }
          ]
        }
      ],
      reviews: [
        { author: "模拟用户 A", score: 5, text: "动作纠正特别细，方便测试评分模块。", time: "3 天前" }
      ]
    },
    {
      id: "coach-demo-b",
      role: "coach",
      name: "模拟教练 B",
      handle: "@demo.coach.b",
      avatar: "周",
      avatarImage: createPortraitAvatar({ skin: "#f2c8ad", hair: "#5c3e2e", shirt: "#5f7fa0", bgA: "#f3dbc9", bgB: "#d2a48d" }),
      city: "厦门",
      locationLabel: "厦门 · 湖里区",
      lat: 24.5002,
      lng: 118.1184,
      bio: "模拟教练 B 用于测试普拉提恢复类课程、套餐价格和评论功能。",
      shortDesc: "核心激活、体态改善，适合测试恢复类课程。",
      price: "¥238/小时",
      tags: ["模拟教练", "普拉提", "康复"],
      years: "4",
      certifications: ["Balanced Body", "普拉提教练认证"],
      pricingPlans: [
        { title: "普拉提 1v1", detail: "核心激活 + 体态改善", price: "¥238/小时" },
        { title: "恢复课包", detail: "8 节恢复课程", price: "¥1680/8节" },
        { title: "双人普拉提", detail: "适合情侣 / 闺蜜", price: "¥320/小时" }
      ],
      followers: 1460,
      following: 28,
      ratingAvg: 5.0,
      ratingCount: 182,
      listed: true,
      posts: [
        { time: "今天", content: "模拟教练 B 更新了晚间核心激活课时段。", meta: "模拟动态 · 新增课表" }
      ],
      reviews: [
        { author: "模拟用户 B", score: 5, text: "很耐心，适合测试恢复课预约。", time: "2 天前" }
      ]
    }
  ]
    .map((profile) => applyDemoProfilePatch(profile))
    .concat(createSupplementalDemoProfiles());
}

const bookingCards = [];

const appView = document.getElementById("appView");
const overlay = document.getElementById("registerOverlay");
const navLinks = document.querySelectorAll(".nav-link[data-page]");
const fabButton = document.getElementById("fabButton");
const SESSION_STORAGE_KEY = "fithub_trial_session_id";
const SNAPSHOT_STORAGE_KEY = "fithub_trial_snapshot_v2";
const ACCOUNT_STORAGE_KEY = "fithub_trial_accounts_v1";
const PROFILE_BACKUP_STORAGE_KEY = "fithub_trial_profile_backups_v1";
const FOLLOW_BACKUP_STORAGE_KEY = "fithub_trial_follow_backups_v1";
const ACTIVE_ACCOUNT_STORAGE_KEY = "fithub_trial_active_account_v1";
const LOGOUT_MARKER_STORAGE_KEY = "fithub_trial_logged_out_v1";
const MESSAGE_READ_STATE_STORAGE_KEY = "fithub_trial_message_read_state_v1";
const DEFAULT_RUNTIME_CONFIG = Object.freeze(normalizeRuntimeConfig(window.__FITHUB_CONFIG__ || {}));
const DEFAULT_LOCATION_STATUS = "默认城市为厦门，你可以点击顶部城市切换成自己的城市或使用实时定位。";
const REGISTER_WHEEL_ITEM_HEIGHT = 52;
const REGISTER_WHEEL_FIELDS = {
  height_cm: {
    label: "身高",
    unit: "cm",
    min: 140,
    max: 220,
    step: 1,
    defaultValue: 170,
    helper: "上下滑动选择你的身高"
  },
  weight_kg: {
    label: "体重",
    unit: "kg",
    min: 35,
    max: 160,
    step: 0.5,
    defaultValue: 60,
    helper: "用于更准确估算训练消耗"
  }
};

function detectUrlPrefix() {
  const path = window.location.pathname || "/";

  if (path === "/" || path === "/index.html" || path === "/mobile.html") {
    return "";
  }

  if (/\.[a-z0-9]+$/i.test(path)) {
    const index = path.lastIndexOf("/");
    return index > 0 ? path.slice(0, index) : "";
  }

  return path.replace(/\/+$/, "");
}

const URL_PREFIX = detectUrlPrefix();
const APP_CONFIG = window.__FITHUB_CONFIG__ || {};
const EXTERNAL_API_ORIGIN = String(APP_CONFIG.apiOrigin || "").trim().replace(/\/+$/, "");
const API_BASE = EXTERNAL_API_ORIGIN ? `${EXTERNAL_API_ORIGIN}/api` : `${URL_PREFIX}/api`;

const state = {
  activePage: "home",
  activeHomeTab: "gym",
  searchKeyword: "",
  userPosition: {
    ...CITY_PRESETS.xiamen,
    source: "default"
  },
  locationStatus: "默认城市为厦门，你可以点击顶部城市切换成自己的城市或使用实时定位。",
  overlayMode: null,
  selectedRole: "enthusiast",
  registerRole: "enthusiast",
  registerSuccess: "",
  registerUploadDrafts: {},
  registerFormDrafts: {},
  registerWheelField: "",
  managedAccounts: [],
  authRole: "enthusiast",
  authPhone: "",
  authMessage: "",
  authMatches: [],
  authAccountId: "",
  authRestoreToken: "",
  authVerificationCode: "",
  authCodeCooldownUntil: 0,
  authCodeHint: "",
  registerCodeCooldownUntil: 0,
  cityInput: "",
  profiles: createInitialProfiles(),
  managedProfileIds: [],
  currentActorProfileId: "",
  activeProfileId: "",
  followSet: new Set(),
  followerSet: new Set(),
  favoritePostIds: new Set(),
  favoritePosts: [],
  notifications: [],
  likeMutationQueue: new Map(),
  favoriteMutationQueue: new Map(),
  pendingMessageProfileIds: new Set(),
  ratingDrafts: {},
  reviewDrafts: {},
  commentDrafts: {},
  overlayReturnMode: null,
  profileReturnPage: "home",
  profileSubpage: "",
  composeProfileId: "",
  composeContent: "",
  composeMeta: "",
  composeMedia: [],
  mediaViewerPostId: "",
  mediaViewerIndex: 0,
  bookings: bookingCards,
  threads: [],
  checkinEditing: false,
  checkinSelectionDraft: [],
  checkinCurrentSportId: "",
  workoutSession: null,
  workoutFinishing: null,
  pendingFinishedWorkout: null,
  outdoorShareCheckinId: "",
  chatTargetProfileId: "",
  chatDraft: "",
  socialTab: "following",
  healthViewMode: "overview",
  shopCategory: "all",
  sessionId: "",
  runtimeConfig: { ...DEFAULT_RUNTIME_CONFIG },
  isBootstrapping: false
};

const profileSwipe = {
  active: false,
  engaged: false,
  pointerId: null,
  startX: 0,
  startY: 0,
  offset: 0
};

let refreshPromise = null;
let restorePromise = null;
let followRestorePromise = null;
let lastSuccessfulSyncAt = 0;
let authLookupTimeout = null;
let mapSdkPromise = null;
let mapSdkProvider = "";
const routeMapRegistry = new Map();

function escapeHtml(value = "") {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}

function isProvidedFile(value) {
  return Boolean(
    value &&
      typeof value === "object" &&
      "name" in value &&
      "size" in value &&
      value.name &&
      value.size >= 0
  );
}

function getUploadedImageUrl(fileValue, fallbackUrl = "") {
  if (
    isProvidedFile(fileValue) &&
    typeof URL !== "undefined" &&
    typeof URL.createObjectURL === "function"
  ) {
    return URL.createObjectURL(fileValue);
  }
  return fallbackUrl;
}

function getStoredSessionId() {
  try {
    return window.localStorage.getItem(SESSION_STORAGE_KEY) || "";
  } catch (_error) {
    return "";
  }
}

function storeSessionId(sessionId) {
  if (!sessionId) return;
  try {
    window.localStorage.setItem(SESSION_STORAGE_KEY, sessionId);
  } catch (_error) {
    // Ignore storage errors in private browsing modes.
  }
}

function getStoredSnapshot() {
  try {
    const raw = window.localStorage.getItem(SNAPSHOT_STORAGE_KEY);
    return raw ? JSON.parse(raw) : null;
  } catch (_error) {
    return null;
  }
}

function storeSnapshot(payload) {
  if (!payload?.session) return;
  try {
    const previous = getStoredSnapshot();
    const incomingManagedIds = Array.isArray(payload.session.managedProfileIds) ? payload.session.managedProfileIds : [];
    const previousManagedIds = Array.isArray(previous?.session?.managedProfileIds)
      ? previous.session.managedProfileIds
      : [];
    const snapshotToStore =
      !incomingManagedIds.length && previousManagedIds.length ? previous : payload;
    window.localStorage.setItem(SNAPSHOT_STORAGE_KEY, JSON.stringify(snapshotToStore));
  } catch (_error) {
    // Ignore storage quota failures.
  }
}

function getStoredProfileBackups() {
  try {
    const raw = window.localStorage.getItem(PROFILE_BACKUP_STORAGE_KEY);
    const parsed = raw ? JSON.parse(raw) : [];
    return Array.isArray(parsed) ? parsed : [];
  } catch (_error) {
    return [];
  }
}

function storeProfileBackups(items) {
  try {
    window.localStorage.setItem(PROFILE_BACKUP_STORAGE_KEY, JSON.stringify(items));
  } catch (_error) {
    // Ignore storage quota failures.
  }
}

function getStoredFollowBackups() {
  try {
    const raw = window.localStorage.getItem(FOLLOW_BACKUP_STORAGE_KEY);
    const parsed = raw ? JSON.parse(raw) : [];
    return Array.isArray(parsed) ? parsed : [];
  } catch (_error) {
    return [];
  }
}

function storeFollowBackups(items) {
  try {
    window.localStorage.setItem(FOLLOW_BACKUP_STORAGE_KEY, JSON.stringify(items));
  } catch (_error) {
    // Ignore storage quota failures.
  }
}

function getFollowBackupKey({ role = "", phone = "", accountId = "" } = {}) {
  if (accountId && role) return `account:${accountId}:${role}`;
  if (phone && role) return `phone:${phone}:${role}`;
  return "";
}

function rememberFollowBackup(profile, account = null, followSet = state.followSet, followerSet = state.followerSet) {
  const role = profile?.role || "";
  const phone = normalizePhone(account?.phone || profile?.phone || "");
  const accountId = account?.id || account?.accountId || "";
  const key = getFollowBackupKey({ role, phone, accountId });
  if (!roleConfig[role] || !key) return;

  const merged = new Map();
  getStoredFollowBackups().forEach((item) => {
    const itemKey = getFollowBackupKey({
      role: item?.role || "",
      phone: normalizePhone(item?.phone || ""),
      accountId: item?.accountId || ""
    });
    if (itemKey) merged.set(itemKey, item);
  });

  merged.set(key, {
    role,
    phone,
    accountId,
    profileId: profile?.id || "",
    followSet: Array.from(followSet || []).filter(Boolean),
    followerSet: Array.from(followerSet || []).filter(Boolean),
    updatedAt: new Date().toISOString()
  });

  storeFollowBackups(Array.from(merged.values()).slice(0, 18));
}

function findStoredFollowBackup(profile, account = null) {
  const role = profile?.role || "";
  const phone = normalizePhone(account?.phone || profile?.phone || "");
  const accountId = account?.id || account?.accountId || "";
  const preferredKeys = [
    getFollowBackupKey({ role, phone: "", accountId }),
    getFollowBackupKey({ role, phone, accountId: "" })
  ].filter(Boolean);
  const backups = getStoredFollowBackups();
  return backups.find((item) => {
    const itemKey = getFollowBackupKey({
      role: item?.role || "",
      phone: normalizePhone(item?.phone || ""),
      accountId: item?.accountId || ""
    });
    return preferredKeys.includes(itemKey);
  }) || null;
}

function rememberManagedProfileBackups(payload) {
  const managedIds = payload?.session?.managedProfileIds || [];
  const profiles = Array.isArray(payload?.profiles) ? payload.profiles : [];
  if (!managedIds.length || !profiles.length) return;

  const profileMap = new Map(profiles.map((profile) => [profile.id, profile]));
  const merged = new Map();
  getStoredProfileBackups().forEach((item) => {
    const role = item?.role || "";
    const phone = normalizePhone(item?.phone);
    if (!roleConfig[role] || !phone || !item?.profile) return;
    merged.set(`${role}:${phone}`, item);
  });

  managedIds.forEach((profileId) => {
    const profile = profileMap.get(profileId);
    const role = profile?.role || "";
    const phone = normalizePhone(profile?.phone);
    if (!roleConfig[role] || !phone) return;
    merged.set(`${role}:${phone}`, { role, phone, profile });
  });

  storeProfileBackups(Array.from(merged.values()).slice(0, 12));
}

function normalizePhone(value = "") {
  return String(value).replace(/\D+/g, "");
}

function normalizeRuntimeConfig(config = {}) {
  const normalized = {
    mapProvider: String(config?.mapProvider || "").trim().toLowerCase(),
    amapKey: String(config?.amapKey || "").trim(),
    amapSecurityCode: String(config?.amapSecurityCode || "").trim(),
    baiduAk: String(config?.baiduAk || "").trim(),
    mediaStorageProvider: String(config?.mediaStorageProvider || "").trim().toLowerCase(),
    mediaBucket: String(config?.mediaBucket || "").trim(),
    mediaLimits: {
      imageBytes: Number(config?.mediaLimits?.imageBytes) || DEFAULT_MEDIA_LIMITS.imageBytes,
      videoBytes: Number(config?.mediaLimits?.videoBytes) || DEFAULT_MEDIA_LIMITS.videoBytes,
      thumbnailBytes: Number(config?.mediaLimits?.thumbnailBytes) || DEFAULT_MEDIA_LIMITS.thumbnailBytes,
    },
    smsEnabled: Boolean(config?.smsEnabled),
    smsProvider: String(config?.smsProvider || "").trim().toLowerCase()
  };

  if (!normalized.mapProvider) {
    if (normalized.amapKey) normalized.mapProvider = "amap";
    else if (normalized.baiduAk) normalized.mapProvider = "baidu";
  }

  return normalized;
}

function getEffectiveRuntimeConfig() {
  const baseConfig = normalizeRuntimeConfig(window.__FITHUB_CONFIG__ || {});
  const runtimeConfig = normalizeRuntimeConfig(state.runtimeConfig || {});
  return normalizeRuntimeConfig({
    ...baseConfig,
    ...(runtimeConfig.mapProvider ? { mapProvider: runtimeConfig.mapProvider } : {}),
    ...(runtimeConfig.amapKey ? { amapKey: runtimeConfig.amapKey } : {}),
    ...(runtimeConfig.amapSecurityCode ? { amapSecurityCode: runtimeConfig.amapSecurityCode } : {}),
    ...(runtimeConfig.baiduAk ? { baiduAk: runtimeConfig.baiduAk } : {}),
    ...(runtimeConfig.mediaStorageProvider ? { mediaStorageProvider: runtimeConfig.mediaStorageProvider } : {}),
    ...(runtimeConfig.mediaBucket ? { mediaBucket: runtimeConfig.mediaBucket } : {}),
    mediaLimits: {
      ...baseConfig.mediaLimits,
      ...(runtimeConfig.mediaLimits || {}),
    },
    ...(runtimeConfig.smsEnabled ? { smsEnabled: runtimeConfig.smsEnabled } : {}),
    ...(runtimeConfig.smsProvider ? { smsProvider: runtimeConfig.smsProvider } : {})
  });
}

function isSmsVerificationEnabled() {
  return Boolean(getEffectiveRuntimeConfig().smsEnabled);
}

function getSmsSendCooldown(secondsUntil) {
  if (!secondsUntil || secondsUntil <= 0) return "";
  return `${secondsUntil}s 后重发`;
}

function getMediaUploadLimits() {
  return getEffectiveRuntimeConfig().mediaLimits || DEFAULT_MEDIA_LIMITS;
}

function normalizeStoredAccount(item) {
  const roles = Array.isArray(item?.roles)
    ? item.roles.filter((role) => roleConfig[role])
    : item?.role && roleConfig[item.role]
      ? [item.role]
      : [];

  return {
    id: item?.id || item?.accountId || "",
    restoreToken: item?.restoreToken || "",
    phone: normalizePhone(item?.phone),
    roles
  };
}

function getStoredAccounts() {
  try {
    const raw = window.localStorage.getItem(ACCOUNT_STORAGE_KEY);
    const parsed = raw ? JSON.parse(raw) : [];
    if (!Array.isArray(parsed)) return [];
    const merged = new Map();
    parsed
      .map((item) => normalizeStoredAccount(item))
      .filter((item) => (item.id && item.restoreToken) || item.phone)
      .forEach((item) => {
        const key = getStoredAccountKey(item);
        if (!key) return;
        const current = merged.get(key);
        merged.set(key, {
          id: item.id || current?.id || "",
          restoreToken: item.restoreToken || current?.restoreToken || "",
          phone: item.phone || current?.phone || "",
          roles: Array.from(new Set([...(current?.roles || []), ...(item.roles || [])])).filter((role) => roleConfig[role])
        });
      });
    return Array.from(merged.values()).slice(0, 8);
  } catch (_error) {
    return [];
  }
}

function storeAccounts(accounts) {
  try {
    window.localStorage.setItem(ACCOUNT_STORAGE_KEY, JSON.stringify(accounts));
  } catch (_error) {
    // Ignore storage quota failures.
  }
}

function hasLogoutMarker() {
  try {
    return window.localStorage.getItem(LOGOUT_MARKER_STORAGE_KEY) === "1";
  } catch (_error) {
    return false;
  }
}

function setLogoutMarker(enabled) {
  try {
    if (enabled) {
      window.localStorage.setItem(LOGOUT_MARKER_STORAGE_KEY, "1");
    } else {
      window.localStorage.removeItem(LOGOUT_MARKER_STORAGE_KEY);
    }
  } catch (_error) {
    // Ignore storage failures.
  }
}

function getStoredAccountKey(account) {
  if (account.phone) return `phone:${account.phone}`;
  if (account.id) return `id:${account.id}`;
  return "";
}

function getStoredMessageReadState() {
  try {
    const raw = window.localStorage.getItem(MESSAGE_READ_STATE_STORAGE_KEY);
    const parsed = raw ? JSON.parse(raw) : {};
    return parsed && typeof parsed === "object" ? parsed : {};
  } catch (_error) {
    return {};
  }
}

function storeMessageReadState(payload) {
  try {
    window.localStorage.setItem(MESSAGE_READ_STATE_STORAGE_KEY, JSON.stringify(payload));
  } catch (_error) {
    // Ignore storage quota failures.
  }
}

function getActorMessageReadState(profileId = state.currentActorProfileId) {
  const actorId = String(profileId || "");
  if (!actorId) return { notificationsSeenAt: "", threads: {} };
  const stored = getStoredMessageReadState();
  const entry = stored[actorId];
  return {
    notificationsSeenAt: String(entry?.notificationsSeenAt || ""),
    threads: entry?.threads && typeof entry.threads === "object" ? entry.threads : {}
  };
}

function updateActorMessageReadState(profileId, updater) {
  const actorId = String(profileId || "");
  if (!actorId || typeof updater !== "function") return;
  const stored = getStoredMessageReadState();
  const current = {
    notificationsSeenAt: String(stored[actorId]?.notificationsSeenAt || ""),
    threads: stored[actorId]?.threads && typeof stored[actorId].threads === "object" ? { ...stored[actorId].threads } : {}
  };
  const next = updater(current) || current;
  stored[actorId] = {
    notificationsSeenAt: String(next.notificationsSeenAt || ""),
    threads: next.threads && typeof next.threads === "object" ? next.threads : {}
  };
  storeMessageReadState(stored);
}

function getThreadUnreadCount(thread, actorId = state.currentActorProfileId) {
  if (!thread?.id || !Array.isArray(thread.messages) || !actorId) return 0;
  const readState = getActorMessageReadState(actorId);
  const lastReadAt = new Date(readState.threads?.[thread.id] || 0).getTime() || 0;
  return thread.messages.filter((message) => {
    const createdAt = new Date(message.createdAt || 0).getTime() || 0;
    return message.senderProfileId !== actorId && createdAt > lastReadAt;
  }).length;
}

function getUnreadNotificationCount(actorId = state.currentActorProfileId) {
  const notifications = Array.isArray(state.notifications) ? state.notifications : [];
  if (!notifications.length || !actorId) return 0;
  const readState = getActorMessageReadState(actorId);
  const notificationsSeenAt = new Date(readState.notificationsSeenAt || 0).getTime() || 0;
  return notifications.filter((item) => {
    const createdAt = new Date(item.createdAt || 0).getTime() || 0;
    return createdAt > notificationsSeenAt;
  }).length;
}

function getTotalUnreadInboxCount(actorId = state.currentActorProfileId) {
  const threadUnread = (state.threads || []).reduce((total, thread) => total + getThreadUnreadCount(thread, actorId), 0);
  return getUnreadNotificationCount(actorId) + threadUnread;
}

function markNotificationsRead(actorId = state.currentActorProfileId) {
  const notifications = Array.isArray(state.notifications) ? state.notifications : [];
  if (!actorId || !notifications.length) return;
  const latestCreatedAt = notifications
    .map((item) => item?.createdAt || "")
    .filter(Boolean)
    .sort()
    .at(-1);
  if (!latestCreatedAt) return;
  updateActorMessageReadState(actorId, (current) => ({
    ...current,
    notificationsSeenAt: latestCreatedAt
  }));
}

function markThreadRead(threadId, actorId = state.currentActorProfileId) {
  const thread = (state.threads || []).find((item) => item.id === threadId);
  if (!actorId || !thread?.messages?.length) return;
  const latestIncoming = [...thread.messages]
    .filter((message) => message.senderProfileId !== actorId)
    .sort((left, right) => String(left.createdAt || "").localeCompare(String(right.createdAt || "")))
    .at(-1);
  if (!latestIncoming?.createdAt) return;
  updateActorMessageReadState(actorId, (current) => ({
    ...current,
    threads: {
      ...(current.threads || {}),
      [threadId]: latestIncoming.createdAt
    }
  }));
}

function rememberManagedAccounts(accounts = []) {
  if (!accounts.length) return;
  const merged = new Map();

  getStoredAccounts().forEach((item) => {
    const key = getStoredAccountKey(item);
    if (key) merged.set(key, item);
  });

  accounts.forEach((item) => {
    const normalized = normalizeStoredAccount(item);
    const key = getStoredAccountKey(normalized);
    if (!key) return;

    const current = merged.get(key);
    merged.set(key, {
      id: normalized.id || current?.id || "",
      restoreToken: normalized.restoreToken || current?.restoreToken || "",
      phone: normalized.phone || current?.phone || "",
      roles: Array.from(new Set([...(current?.roles || []), ...(normalized.roles || [])])).filter((role) => roleConfig[role])
    });
  });

  storeAccounts(Array.from(merged.values()).slice(0, 8));
}

function rememberAccount(role, phone, accountId = "", restoreToken = "") {
  rememberManagedAccounts([
    {
      id: accountId,
      restoreToken,
      phone,
      roles: role ? [role] : []
    }
  ]);
}

function getStoredAccountForRole(role) {
  return getStoredAccounts().find((item) => item.roles.includes(role)) || null;
}

function normalizeActiveAccount(item) {
  return {
    role: roleConfig[item?.role] ? item.role : "",
    phone: normalizePhone(item?.phone),
    accountId: item?.accountId || item?.id || "",
    restoreToken: item?.restoreToken || "",
    profileId: item?.profileId || ""
  };
}

function getStoredActiveAccount() {
  try {
    const raw = window.localStorage.getItem(ACTIVE_ACCOUNT_STORAGE_KEY);
    return raw ? normalizeActiveAccount(JSON.parse(raw)) : null;
  } catch (_error) {
    return null;
  }
}

function rememberActiveAccount(role, phone, accountId = "", restoreToken = "", profileId = "") {
  const normalized = normalizeActiveAccount({
    role,
    phone,
    accountId,
    restoreToken,
    profileId
  });
  if (!normalized.role && !normalized.phone && !normalized.accountId) return;
  try {
    window.localStorage.setItem(ACTIVE_ACCOUNT_STORAGE_KEY, JSON.stringify(normalized));
  } catch (_error) {
    // Ignore storage quota failures.
  }
}

function getPreferredStoredAccount(role = "") {
  const active = getStoredActiveAccount();
  if (active?.phone && (!role || active.role === role)) {
    return {
      id: active.accountId,
      restoreToken: active.restoreToken,
      phone: active.phone,
      roles: active.role ? [active.role] : []
    };
  }
  return (role ? getStoredAccountForRole(role) : null) || getStoredAccounts()[0] || null;
}

function clearAuthResolution({ preservePhone = true } = {}) {
  state.authMatches = [];
  state.authAccountId = "";
  state.authRestoreToken = "";
  state.authVerificationCode = "";
  state.authCodeHint = "";
  if (!preservePhone) {
    state.authPhone = "";
  }
}

function getRegisterVerificationCode(role = state.registerRole) {
  return getRegisterDraft(role).verification_code || "";
}

async function sendAuthVerificationCode() {
  const phone = normalizePhone(state.authPhone);
  if (phone.length !== 11) {
    throw new Error("请输入正确的 11 位手机号。");
  }
  const payload = await apiRequest(`${API_BASE}/auth/send-code`, {
    method: "POST",
    body: {
      sessionId: state.sessionId || getStoredSessionId(),
      phone,
      purpose: "login"
    }
  });
  state.authCodeCooldownUntil = Date.now() + Number(payload.cooldownSeconds || 60) * 1000;
  state.authCodeHint = payload.debugCode ? `测试验证码：${payload.debugCode}` : "验证码已发送，请查收短信。";
  state.authMessage = state.authCodeHint;
  renderOverlay();
}

async function sendRegisterVerificationCode(role = state.registerRole) {
  const phone = normalizePhone(getRegisterDraft(role).phone || "");
  if (phone.length !== 11) {
    throw new Error("请先填写正确的 11 位手机号。");
  }
  const payload = await apiRequest(`${API_BASE}/auth/send-code`, {
    method: "POST",
    body: {
      sessionId: state.sessionId || getStoredSessionId(),
      phone,
      purpose: "register"
    }
  });
  state.registerCodeCooldownUntil = Date.now() + Number(payload.cooldownSeconds || 60) * 1000;
  setRegisterDraftValue(role, "verification_code", getRegisterDraft(role).verification_code || "");
  state.authCodeHint = payload.debugCode ? `测试验证码：${payload.debugCode}` : "验证码已发送，请查收短信。";
  state.registerSuccess = state.authCodeHint;
  renderOverlay();
}

async function lookupAuthMatches(phone, { silent = false } = {}) {
  const normalizedPhone = normalizePhone(phone);
  if (!normalizedPhone) {
    state.authMatches = [];
    if (!silent) {
      state.authMessage = "";
      renderOverlay();
    }
    return [];
  }

  const payload = await apiRequest(`${API_BASE}/auth/lookup-phone`, {
    method: "POST",
    body: {
      sessionId: state.sessionId || getStoredSessionId(),
      phone: normalizedPhone
    }
  });

  state.authMatches = Array.isArray(payload?.matches) ? payload.matches : [];

  if (!state.authMatches.length) {
    if (!silent) {
      state.authMessage = "这个手机号暂时没有查到已注册身份，请确认号码是否填写正确。";
      renderOverlay();
    }
    return [];
  }

  const matchedRole = state.authMatches.find((item) => item.role === state.authRole);
  if (!matchedRole) {
    state.authRole = state.authMatches[0].role;
  }

  if (!silent) {
    state.authMessage = `已识别到这个手机号下的 ${state.authMatches.length} 个身份，请选择要登录的身份。`;
    renderOverlay();
  }

  return state.authMatches;
}

function findRecoverableSnapshotProfile(role, phone, profileId = "") {
  const phoneKey = normalizePhone(phone);
  if (!roleConfig[role] || !phoneKey) return null;

  const backups = getStoredProfileBackups();
  const exactBackup = profileId
    ? backups.find((item) => item?.profile?.id === profileId)
    : null;
  const backup = exactBackup || backups.find((item) => {
    return item?.role === role && normalizePhone(item?.phone) === phoneKey && item?.profile;
  });
  if (backup?.profile) {
    return backup.profile;
  }

  const snapshot = getStoredSnapshot();
  const profiles = Array.isArray(snapshot?.profiles) ? snapshot.profiles : [];
  const managedIds = new Set(snapshot?.session?.managedProfileIds || []);

  const exactProfile = profileId ? profiles.find((profile) => profile?.id === profileId) : null;
  return (
    exactProfile || profiles.find((profile) => {
      if (!profile || profile.role !== role) return false;
      if (normalizePhone(profile.phone) !== phoneKey) return false;
      return !managedIds.size || managedIds.has(profile.id);
    }) || null
  );
}

function buildSnapshotRecoveryProfile(profile) {
  if (!profile) return null;
  return {
    name: profile.name || "",
    phone: normalizePhone(profile.phone),
    city: profile.city || state.userPosition.city,
    locationLabel: profile.locationLabel || state.userPosition.label,
    avatarImage: profile.avatarImage || "",
    intro: profile.bio || profile.shortDesc || "",
    level: profile.level || "",
    goal: profile.goal || "",
    gender: profile.gender || "",
    heightCm: profile.heightCm || "",
    weightKg: profile.weightKg || "",
    bodyFat: profile.bodyFat || "",
    favoriteSports: Array.isArray(profile.favoriteSports) ? profile.favoriteSports : [],
    connectedDevices: Array.isArray(profile.connectedDevices) ? profile.connectedDevices : [],
    healthSource: profile.healthSource || "",
    deviceSyncedAt: profile.deviceSyncedAt || "",
    healthSnapshot: profile.healthSnapshot || {},
    healthHistory: Array.isArray(profile.healthHistory) ? profile.healthHistory : [],
    restingHeartRate: profile.restingHeartRate || "",
    price: profile.price || "",
    hours: profile.hours || "",
    contactName: profile.contactName || "",
    years: profile.years || "",
    certifications: Array.isArray(profile.certifications)
      ? profile.certifications.join(" ")
      : profile.certifications || "",
    specialties: Array.isArray(profile.tags) ? profile.tags.join(" ") : "",
    facilities: Array.isArray(profile.tags) ? profile.tags.join(" ") : "",
    pricingPlans: Array.isArray(profile.pricingPlans) ? profile.pricingPlans : [],
    checkins: Array.isArray(profile.checkins) ? profile.checkins : [],
    reviews: Array.isArray(profile.reviews) ? profile.reviews : []
  };
}

async function recoverAccountFromSnapshot(role, phone) {
  const preferred = getStoredActiveAccount();
  const cachedProfile = findRecoverableSnapshotProfile(role, phone, preferred?.profileId || "");
  if (!cachedProfile) return false;

  await postAndSync(`${API_BASE}/auth/recover-local`, {
    sessionId: state.sessionId,
    role,
    phone: normalizePhone(phone),
    profile: buildSnapshotRecoveryProfile(cachedProfile),
    posts: Array.isArray(cachedProfile.posts) ? cachedProfile.posts : [],
    checkins: Array.isArray(cachedProfile.checkins) ? cachedProfile.checkins : []
  }, { keepOverlay: true });

  await maybeRestoreFollowState({ force: true }).catch(() => false);

  state.authMessage = "线上没找到这个身份，已从这台设备的本地缓存恢复到线上。";
  return true;
}

function bootstrapRememberedAccountLocally() {
  const preferred = getStoredActiveAccount();
  const remembered = getPreferredStoredAccount(preferred?.role || state.selectedRole);
  if (!remembered) return false;

  const role = preferred?.role || remembered.roles?.[0] || state.selectedRole;
  const phone = preferred?.phone || remembered.phone;
  if (!roleConfig[role] || !phone) return false;

  const cachedProfile = findRecoverableSnapshotProfile(role, phone, preferred?.profileId || "");
  if (!cachedProfile?.id) return false;

  const snapshot = getStoredSnapshot();
  const baseProfiles = Array.isArray(snapshot?.profiles) && snapshot.profiles.length
    ? snapshot.profiles
    : createInitialProfiles();
  const mergedProfiles = [...baseProfiles.filter((item) => item?.id !== cachedProfile.id), cachedProfile];
  const account = normalizeStoredAccount({
    id: preferred?.accountId || remembered.id || "",
    restoreToken: preferred?.restoreToken || remembered.restoreToken || "",
    phone,
    roles: [role]
  });

  syncStateFromServer(
    {
      config: state.runtimeConfig,
      session: {
        id: state.sessionId || getStoredSessionId() || `session-local-${Math.random().toString(16).slice(2, 10)}`,
        selectedRole: role,
        managedProfileIds: [cachedProfile.id],
        managedAccounts: [account],
        currentActorProfileId: cachedProfile.id,
        userPosition: snapshot?.session?.userPosition || state.userPosition,
        locationStatus: "已从这个设备恢复上次登录的账号。"
      },
      profiles: mergedProfiles,
      followSet: snapshot?.followSet || [],
      followerSet: snapshot?.followerSet || [],
      favoritePostIds: snapshot?.favoritePostIds || [],
      favoritePosts: snapshot?.favoritePosts || [],
      notifications: snapshot?.notifications || [],
      bookings: snapshot?.bookings || [],
      threads: snapshot?.threads || []
    },
    { keepOverlay: true }
  );

  state.locationStatus = "已从这个设备恢复上次登录的账号。";
  return true;
}

function clearStaleManagedSession({ keepStoredAccounts = true } = {}) {
  state.managedProfileIds = [];
  state.managedAccounts = keepStoredAccounts ? getStoredAccounts() : [];
  state.currentActorProfileId = "";
  state.activeProfileId = "";
  state.composeProfileId = "";
  state.followSet = new Set();
  state.followerSet = new Set();
  state.favoritePostIds = new Set();
  state.favoritePosts = [];
  state.notifications = [];
  state.bookings = [];
  state.threads = [];
  state.selectedRole = "enthusiast";
  state.registerRole = "enthusiast";
  if (!keepStoredAccounts) {
    clearAuthResolution({ preservePhone: false });
  }
}

async function maybeRestoreRememberedAccounts({ force = false } = {}) {
  if (hasLogoutMarker()) return false;
  if (state.managedProfileIds.length && !force) return false;
  const preferred = getStoredActiveAccount();
  const accounts = getStoredAccounts().sort((left, right) => {
    const leftScore = preferred && left.phone === preferred.phone ? 1 : 0;
    const rightScore = preferred && right.phone === preferred.phone ? 1 : 0;
    return rightScore - leftScore;
  });
  const storedProfileBackups = getStoredProfileBackups();
  if (!accounts.length && !storedProfileBackups.length) return false;
  if (restorePromise) return restorePromise;

  restorePromise = apiRequest(`${API_BASE}/auth/restore`, {
    method: "POST",
    body: {
      sessionId: state.sessionId || getStoredSessionId(),
      accounts: accounts.map((item) => ({
        accountId: item.id,
        restoreToken: item.restoreToken,
        phone: item.phone,
        role: item.roles[0] || ""
      })),
      selectedRole: state.selectedRole,
      currentActorProfileId: state.currentActorProfileId
    }
  })
    .then(async (payload) => {
      if (payload?.session?.managedProfileIds?.length) {
        syncStateFromServer(payload, { keepOverlay: true });
        state.locationStatus = "已恢复这个设备保存的账户记录。";
        return true;
      }
      const recoveryCandidates = [];
      if (preferred?.role && preferred?.phone) {
        recoveryCandidates.push({ role: preferred.role, phone: preferred.phone });
      }
      accounts.forEach((item) => {
        (item.roles || []).forEach((role) => {
          recoveryCandidates.push({ role, phone: item.phone });
        });
      });
      storedProfileBackups.forEach((item) => {
        recoveryCandidates.push({ role: item?.role || "", phone: item?.phone || "" });
      });
      for (const candidate of recoveryCandidates) {
        if (!roleConfig[candidate.role] || !normalizePhone(candidate.phone)) continue;
        if (await recoverAccountFromSnapshot(candidate.role, candidate.phone)) {
          return true;
        }
      }
      return false;
    })
    .catch(async () => {
      const recoveryCandidates = [];
      if (preferred?.role && preferred?.phone) {
        recoveryCandidates.push({ role: preferred.role, phone: preferred.phone });
      }
      accounts.forEach((item) => {
        (item.roles || []).forEach((role) => {
          recoveryCandidates.push({ role, phone: item.phone });
        });
      });
      storedProfileBackups.forEach((item) => {
        recoveryCandidates.push({ role: item?.role || "", phone: item?.phone || "" });
      });
      for (const candidate of recoveryCandidates) {
        if (!roleConfig[candidate.role] || !normalizePhone(candidate.phone)) continue;
        if (await recoverAccountFromSnapshot(candidate.role, candidate.phone)) {
          return true;
        }
      }
      return false;
    })
    .finally(() => {
      restorePromise = null;
    });

  return restorePromise;
}

async function maybeRestoreFollowState({ force = false } = {}) {
  if (followRestorePromise) return followRestorePromise;
  const actor = getCurrentActor();
  if (!actor || !state.managedProfileIds.length) return false;
  if (state.followSet.size && !force) return false;

  const matchedAccount =
    state.managedAccounts.find(
      (item) =>
        item.roles.includes(actor.role) &&
        (!normalizePhone(actor.phone) || item.phone === normalizePhone(actor.phone))
    ) || state.managedAccounts[0] || null;

  const backup = findStoredFollowBackup(actor, matchedAccount);
  const targetProfileIds = Array.isArray(backup?.followSet) ? backup.followSet.filter(Boolean) : [];
  if (!targetProfileIds.length) return false;

  followRestorePromise = postAndSync(`${API_BASE}/auth/restore-follows`, {
    profileId: actor.id,
    targetProfileIds
  }, { keepOverlay: true })
    .then(() => {
      state.locationStatus = "已恢复这个账号之前关注的对象。";
      return true;
    })
    .catch(() => false)
    .finally(() => {
      followRestorePromise = null;
    });

  return followRestorePromise;
}

function shouldRetryAfterRestore(error) {
  const message = String(error?.message || "");
  return (
    message.includes("请先注册后再关注") ||
    message.includes("请先注册自己的训练者身份") ||
    message.includes("只能用当前设备已注册的身份") ||
    message.includes("请先注册后再") ||
    message.includes("请先用健身爱好者身份注册")
  );
}

async function apiRequest(path, { method = "GET", body } = {}) {
  const response = await fetch(path, {
    method,
    headers: body ? { "Content-Type": "application/json" } : undefined,
    body: body ? JSON.stringify(body) : undefined
  });

  const payload = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new Error(payload.error || "请求失败，请稍后再试。");
  }
  return payload;
}

function syncStateFromServer(payload, { keepOverlay = false } = {}) {
  if (!payload?.session) return;
  const incomingManagedIds = Array.isArray(payload.session.managedProfileIds) ? payload.session.managedProfileIds : [];
  const preserveManagedSession = !incomingManagedIds.length && state.managedProfileIds.length > 0;
  const previousManagedIds = [...state.managedProfileIds];
  const previousManagedAccounts = [...state.managedAccounts];
  const previousCurrentActorProfileId = state.currentActorProfileId;
  const previousSelectedRole = state.selectedRole;
  const previousRegisterRole = state.registerRole;
  const previousFollowSet = new Set(state.followSet);
  const previousFollowerSet = new Set(state.followerSet);
  const previousFavoritePostIds = new Set(state.favoritePostIds);
  const previousFavoritePosts = [...state.favoritePosts];
  const previousNotifications = [...state.notifications];
  const previousBookings = [...state.bookings];
  const previousThreads = [...state.threads];
  const incomingProfiles = enhanceProfiles(payload.profiles || []);
  const mergedProfileMap = new Map(incomingProfiles.map((profile) => [profile.id, profile]));

  if (preserveManagedSession) {
    state.profiles.forEach((profile) => {
      if (profile?.id && previousManagedIds.includes(profile.id) && !mergedProfileMap.has(profile.id)) {
        mergedProfileMap.set(profile.id, profile);
      }
    });
  }

  state.sessionId = payload.session.id || state.sessionId;
  state.runtimeConfig = normalizeRuntimeConfig({
    ...state.runtimeConfig,
    ...(payload.config || {})
  });
  storeSessionId(state.sessionId);
  state.selectedRole = preserveManagedSession ? previousSelectedRole : payload.session.selectedRole || state.selectedRole;
  state.registerRole = preserveManagedSession ? previousRegisterRole : payload.session.selectedRole || state.registerRole;
  state.userPosition = payload.session.userPosition || state.userPosition;
  state.locationStatus = payload.session.locationStatus || state.locationStatus;
  state.profiles = Array.from(mergedProfileMap.values());
  state.managedProfileIds = preserveManagedSession ? previousManagedIds : payload.session.managedProfileIds || [];
  state.managedAccounts = preserveManagedSession
    ? previousManagedAccounts
    : (payload.session.managedAccounts || []).map((item) => normalizeStoredAccount(item));
  if (state.managedAccounts.length) {
    rememberManagedAccounts(state.managedAccounts);
  }
  rememberManagedProfileBackups(payload);
  state.currentActorProfileId = preserveManagedSession
    ? previousCurrentActorProfileId || previousManagedIds[0] || ""
    : payload.session.currentActorProfileId || state.managedProfileIds[0] || "";
  state.followSet = preserveManagedSession ? previousFollowSet : new Set(payload.followSet || []);
  state.followerSet = preserveManagedSession ? previousFollowerSet : new Set(payload.followerSet || []);
  state.favoritePostIds = preserveManagedSession ? previousFavoritePostIds : new Set(payload.favoritePostIds || []);
  state.favoritePosts = preserveManagedSession ? previousFavoritePosts : (Array.isArray(payload.favoritePosts) ? payload.favoritePosts : []);
  state.notifications = preserveManagedSession ? previousNotifications : (Array.isArray(payload.notifications) ? payload.notifications : []);
  state.bookings = preserveManagedSession ? previousBookings : (payload.bookings || []);
  state.threads = preserveManagedSession ? previousThreads : (payload.threads || []);
  state.composeProfileId = state.composeProfileId || state.currentActorProfileId || state.managedProfileIds[0] || "";

  const activeProfile = getProfile(state.currentActorProfileId || state.managedProfileIds[0] || "");
  if (activeProfile) {
    const matchedAccount =
      state.managedAccounts.find(
        (item) =>
          item.roles.includes(activeProfile.role) &&
          (!normalizePhone(activeProfile.phone) || item.phone === normalizePhone(activeProfile.phone))
      ) || state.managedAccounts[0];
    rememberActiveAccount(
      activeProfile.role,
      matchedAccount?.phone || activeProfile.phone || "",
      matchedAccount?.id || "",
      matchedAccount?.restoreToken || "",
      activeProfile.id || ""
    );
    rememberFollowBackup(activeProfile, matchedAccount, state.followSet, state.followerSet);
  }

  const myProfile = getMyPageProfile();
  const availableSportIds = new Set((myProfile?.favoriteSports || []).map((item) => item));
  if (!availableSportIds.has(state.checkinCurrentSportId)) {
    state.checkinCurrentSportId = myProfile?.favoriteSports?.[0] || "";
  }

  if (!state.activeProfileId || !getProfile(state.activeProfileId)) {
    state.activeProfileId = state.currentActorProfileId || state.managedProfileIds[0] || "";
  }

  if (!keepOverlay) {
    if (!state.managedProfileIds.length) {
      state.overlayMode = "welcome";
    } else if (state.overlayMode === "welcome") {
      state.overlayMode = null;
    }
  }

  if (!preserveManagedSession) {
    storeSnapshot(payload);
  }
  if (state.managedProfileIds.length) {
    setLogoutMarker(false);
  }
}

async function refreshSharedState({ keepOverlay = false } = {}) {
  if (refreshPromise) return refreshPromise;
  const query = state.sessionId || getStoredSessionId();
  const suffix = query ? `?session_id=${encodeURIComponent(query)}` : "";
  refreshPromise = apiRequest(`${API_BASE}/bootstrap${suffix}`)
    .then(async (payload) => {
      syncStateFromServer(payload, { keepOverlay });
      const backendManagedIds = Array.isArray(payload?.session?.managedProfileIds) ? payload.session.managedProfileIds : [];
      if (!backendManagedIds.length && getStoredAccounts().length) {
        const restored = await maybeRestoreRememberedAccounts({ force: true });
        if (!restored) {
          clearStaleManagedSession({ keepStoredAccounts: true });
          state.overlayMode = "welcome";
          state.locationStatus = "这个设备的登录状态已过期，请重新登录。";
        } else {
          await maybeRestoreFollowState();
        }
      } else {
        await maybeRestoreRememberedAccounts();
      }
      state.isBootstrapping = false;
      window.__FITHUB_BOOTSTRAP_DONE__ = true;
      lastSuccessfulSyncAt = Date.now();
      renderPage();
      return payload;
    })
    .finally(() => {
      refreshPromise = null;
    });
  return refreshPromise;
}

async function postAndSync(path, body, { keepOverlay = false } = {}) {
  const requestBody = {
    sessionId: state.sessionId || getStoredSessionId(),
    ...body
  };

  let payload;
  try {
    payload = await apiRequest(path, {
      method: "POST",
      body: requestBody
    });
  } catch (error) {
    if ((getStoredAccounts().length || getStoredProfileBackups().length) && shouldRetryAfterRestore(error)) {
      const restored = await maybeRestoreRememberedAccounts({ force: true });
      if (restored) {
        payload = await apiRequest(path, {
          method: "POST",
          body: {
            sessionId: state.sessionId || getStoredSessionId(),
            ...body
          }
        });
      } else {
        throw error;
      }
    } else {
      throw error;
    }
  }
  syncStateFromServer(payload, { keepOverlay });
  state.isBootstrapping = false;
  return payload;
}

async function postWithoutStateSync(path, body) {
  const requestBody = {
    sessionId: state.sessionId || getStoredSessionId(),
    compact: true,
    ...body
  };

  try {
    return await apiRequest(path, {
      method: "POST",
      body: requestBody
    });
  } catch (error) {
    if ((getStoredAccounts().length || getStoredProfileBackups().length) && shouldRetryAfterRestore(error)) {
      const restored = await maybeRestoreRememberedAccounts({ force: true });
      if (restored) {
        return apiRequest(path, {
          method: "POST",
          body: {
            sessionId: state.sessionId || getStoredSessionId(),
            compact: true,
            ...body
          }
        });
      }
    }
    throw error;
  }
}

function clearStoredAuthArtifacts() {
  [
    SESSION_STORAGE_KEY,
    SNAPSHOT_STORAGE_KEY,
    ACCOUNT_STORAGE_KEY,
    PROFILE_BACKUP_STORAGE_KEY,
    FOLLOW_BACKUP_STORAGE_KEY,
    ACTIVE_ACCOUNT_STORAGE_KEY
  ].forEach((key) => {
    try {
      window.localStorage.removeItem(key);
    } catch (_error) {
      // Ignore storage failures.
    }
  });
}

async function logoutCurrentDevice() {
  try {
    await apiRequest(`${API_BASE}/auth/logout`, {
      method: "POST",
      body: {
        sessionId: state.sessionId || getStoredSessionId()
      }
    });
  } catch (_error) {
    // Local cleanup still matters even if the backend session is already gone.
  }

  clearStoredAuthArtifacts();
  setLogoutMarker(true);
  state.managedAccounts = [];
  state.managedProfileIds = [];
  state.currentActorProfileId = "";
  state.activeProfileId = "";
  state.composeProfileId = "";
  state.followSet = new Set();
  state.followerSet = new Set();
  state.favoritePostIds = new Set();
  state.favoritePosts = [];
  state.notifications = [];
  state.bookings = [];
  state.threads = [];
  state.authPhone = "";
  state.authMessage = "";
  state.authMatches = [];
  state.authAccountId = "";
  state.authRestoreToken = "";
  state.selectedRole = "enthusiast";
  state.registerRole = "enthusiast";
  state.activePage = "home";
  state.overlayMode = "welcome";
  state.profileSubpage = "";
  state.profileReturnPage = "home";
  state.locationStatus = DEFAULT_LOCATION_STATUS;
  state.sessionId = "";
  renderPage();
  refreshSharedState({ keepOverlay: false }).catch(() => {});
}

function readFileAsDataUrl(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => resolve(reader.result);
    reader.onerror = () => reject(new Error("文件读取失败，请重试。"));
    reader.readAsDataURL(file);
  });
}

function optimizeImageFile(file, { maxEdge = 720, quality = 0.82 } = {}) {
  if (!file?.type?.startsWith("image/")) {
    return readFileAsDataUrl(file);
  }

  return new Promise((resolve) => {
    const objectUrl = URL.createObjectURL(file);
    const image = new Image();

    const fallback = () => {
      URL.revokeObjectURL(objectUrl);
      readFileAsDataUrl(file).then(resolve);
    };

    image.onload = () => {
      const ratio = Math.min(1, maxEdge / Math.max(image.width || maxEdge, image.height || maxEdge));
      const width = Math.max(1, Math.round((image.width || maxEdge) * ratio));
      const height = Math.max(1, Math.round((image.height || maxEdge) * ratio));
      const canvas = document.createElement("canvas");
      canvas.width = width;
      canvas.height = height;
      const context = canvas.getContext("2d");

      if (!context) {
        fallback();
        return;
      }

      context.drawImage(image, 0, 0, width, height);
      URL.revokeObjectURL(objectUrl);
      resolve(canvas.toDataURL("image/jpeg", quality));
    };

    image.onerror = fallback;
    image.src = objectUrl;
  });
}

function createVideoPosterDataUrl(file, { maxEdge = 480, quality = 0.78, seekSeconds = 0.2 } = {}) {
  if (!file?.type?.startsWith("video/")) {
    return Promise.resolve("");
  }

  return new Promise((resolve) => {
    const objectUrl = URL.createObjectURL(file);
    const video = document.createElement("video");
    video.muted = true;
    video.playsInline = true;
    video.preload = "metadata";

    const cleanup = () => {
      URL.revokeObjectURL(objectUrl);
      video.removeAttribute("src");
      video.load();
    };

    const fallback = () => {
      cleanup();
      resolve("");
    };

    video.addEventListener("error", fallback, { once: true });
    video.addEventListener(
      "loadeddata",
      () => {
        try {
          if (Number.isFinite(video.duration) && video.duration > seekSeconds) {
            video.currentTime = seekSeconds;
            return;
          }
        } catch (_error) {
          // ignore seek issue and capture current frame
        }
        captureFrame();
      },
      { once: true }
    );

    video.addEventListener("seeked", captureFrame, { once: true });

    function captureFrame() {
      try {
        const width = video.videoWidth || maxEdge;
        const height = video.videoHeight || maxEdge;
        const ratio = Math.min(1, maxEdge / Math.max(width, height));
        const canvas = document.createElement("canvas");
        canvas.width = Math.max(1, Math.round(width * ratio));
        canvas.height = Math.max(1, Math.round(height * ratio));
        const context = canvas.getContext("2d");
        if (!context) {
          fallback();
          return;
        }
        context.drawImage(video, 0, 0, canvas.width, canvas.height);
        const poster = canvas.toDataURL("image/jpeg", quality);
        cleanup();
        resolve(poster);
      } catch (_error) {
        fallback();
      }
    }

    video.src = objectUrl;
  });
}

function getMediaThumbnailUrl(item, kind = "feed") {
  const thumbnailUrl = item?.thumbnailUrl || item?.posterUrl || "";
  const sourceUrl = thumbnailUrl || item?.url || "";
  if (!sourceUrl) return "";
  return optimizeRemoteImageUrl(sourceUrl, kind);
}

function getMediaDisplayUrl(item) {
  return item?.url || "";
}

function formatMediaSize(bytes) {
  const numeric = Number(bytes || 0);
  if (!Number.isFinite(numeric) || numeric <= 0) return "";
  if (numeric < 1024) return `${Math.round(numeric)} B`;
  if (numeric < 1024 * 1024) return `${(numeric / 1024).toFixed(1).replace(/\.0$/, "")} KB`;
  return `${(numeric / (1024 * 1024)).toFixed(1).replace(/\.0$/, "")} MB`;
}

function serializeManagedMediaItem(item) {
  if (!item || !item.url) return null;
  return {
    type: item.type,
    url: item.url,
    name: item.name || "",
    contentType: item.contentType || "",
    sizeBytes: item.sizeBytes || 0,
    storageProvider: item.storageProvider || "",
    storagePath: item.storagePath || "",
    thumbnailUrl: item.thumbnailUrl || item.posterUrl || "",
    thumbnailName: item.thumbnailName || "",
    thumbnailContentType: item.thumbnailContentType || "",
    thumbnailStorageProvider: item.thumbnailStorageProvider || "",
    thumbnailStoragePath: item.thumbnailStoragePath || "",
    thumbnailSizeBytes: item.thumbnailSizeBytes || 0,
  };
}

async function deleteManagedMediaItems(items, { silent = false } = {}) {
  const payloadItems = (Array.isArray(items) ? items : [items])
    .map((item) => serializeManagedMediaItem(item))
    .filter(Boolean);

  if (!payloadItems.length) return { deletedPaths: [] };

  try {
    const payload = await apiRequest(`${API_BASE}/media/delete`, {
      method: "POST",
      body: {
        sessionId: state.sessionId || getStoredSessionId(),
        items: payloadItems,
      },
    });
    if (payload?.config) {
      state.runtimeConfig = normalizeRuntimeConfig({
        ...state.runtimeConfig,
        ...payload.config,
      });
    }
    return payload || { deletedPaths: [] };
  } catch (error) {
    if (!silent) {
      throw error;
    }
    return { deletedPaths: [], error };
  }
}

async function cleanupComposeDraftMedia(items = state.composeMedia) {
  const mediaItems = Array.isArray(items) ? items.filter(Boolean) : [];
  if (!mediaItems.length) return;
  await deleteManagedMediaItems(mediaItems, { silent: true });
}

function getMediaViewerEntry() {
  const found = getPostById(state.mediaViewerPostId);
  if (!found?.post?.media?.length) return null;
  const post = found.post;
  const profile = found.profile || getProfile(post.authorProfileId) || null;
  const total = post.media.length;
  const index = Math.min(Math.max(0, Number(state.mediaViewerIndex || 0)), total - 1);
  const item = post.media[index];
  if (!item) return null;
  return {
    profile,
    post,
    total,
    index,
    item,
  };
}

function openMediaViewer(postId, index = 0) {
  const found = getPostById(postId);
  if (!found?.post?.media?.length) return;
  state.mediaViewerPostId = postId;
  state.mediaViewerIndex = Math.min(Math.max(0, Number(index || 0)), found.post.media.length - 1);
  openOverlay("media");
}

async function readSingleFile(inputName, formData) {
  const draftPreview = state.registerUploadDrafts?.[inputName]?.preview;
  const value = formData.get(inputName);
  if (!isProvidedFile(value) || !value.size) return "";
  const dataUrl = draftPreview || await optimizeImageFile(value, { maxEdge: 360, quality: 0.72 });
  const uploaded = await uploadManagedMedia({
    dataUrl,
    fileName: value.name || `${inputName}.jpg`,
    assetType: "image",
    category: "avatars"
  });
  return uploaded.url;
}

async function uploadManagedMedia({ dataUrl, fileName, assetType, category, thumbnailDataUrl = "", thumbnailName = "" }) {
  const payload = await apiRequest(`${API_BASE}/media/upload`, {
    method: "POST",
    body: {
      sessionId: state.sessionId || getStoredSessionId(),
      dataUrl,
      fileName,
      assetType,
      category,
      thumbnailDataUrl,
      thumbnailName,
    }
  });

  if (payload?.config) {
    state.runtimeConfig = normalizeRuntimeConfig({
      ...state.runtimeConfig,
      ...payload.config
    });
  }

  if (!payload?.media?.url) {
    throw new Error("媒体上传失败，请稍后再试。");
  }

  return payload.media;
}

async function readMediaFiles(files) {
  const media = [];
  const skipped = [];
  const limits = getMediaUploadLimits();
  for (const file of files) {
    if (!isProvidedFile(file) || !file.size) continue;
    const isVideo = file.type.startsWith("video/");
    const maxBytes = isVideo ? limits.videoBytes : limits.imageBytes;
    if (file.size > maxBytes) {
      skipped.push(`${file.name} 过大`);
      continue;
    }
    const url = file.type.startsWith("image/")
      ? await optimizeImageFile(file, { maxEdge: 1440, quality: 0.84 })
      : await readFileAsDataUrl(file);
    const thumbnailDataUrl = file.type.startsWith("image/")
      ? await optimizeImageFile(file, { maxEdge: 480, quality: 0.72 })
      : await createVideoPosterDataUrl(file, { maxEdge: 480, quality: 0.78 });
    const uploaded = await uploadManagedMedia({
      dataUrl: url,
      fileName: file.name,
      assetType: isVideo ? "video" : "image",
      category: "posts",
      thumbnailDataUrl,
      thumbnailName: `${file.name.replace(/\.[^.]+$/, "") || "thumb"}-thumb.jpg`,
    });
    media.push({
      type: isVideo ? "video" : "image",
      url: uploaded.url,
      name: uploaded.name || file.name,
      storageProvider: uploaded.storageProvider || "",
      storagePath: uploaded.storagePath || "",
      contentType: uploaded.contentType || file.type || "",
      sizeBytes: uploaded.sizeBytes || file.size || 0,
      thumbnailUrl: uploaded.thumbnailUrl || "",
      thumbnailName: uploaded.thumbnailName || "",
      thumbnailContentType: uploaded.thumbnailContentType || "",
      thumbnailStorageProvider: uploaded.thumbnailStorageProvider || "",
      thumbnailStoragePath: uploaded.thumbnailStoragePath || "",
      thumbnailSizeBytes: uploaded.thumbnailSizeBytes || 0,
    });
  }
  if (skipped.length) {
    showError(`以下文件暂未加入：${skipped.join("，")}。建议选择更短的视频或更小的图片。`);
  }
  return media;
}

async function buildRegistrationPayload(role, formData) {
  const avatarImage = await readSingleFile("avatar_file", formData);
  const base = {
    avatarImage,
    city: (formData.get("city") || state.userPosition.city || CITY_PRESETS.xiamen.city).toString(),
    locationLabel: (formData.get("location") || state.userPosition.label || CITY_PRESETS.xiamen.label).toString(),
    lat: state.userPosition.lat,
    lng: state.userPosition.lng
  };

  if (role === "gym") {
    return {
      ...base,
      gymName: (formData.get("gym_name") || "").toString(),
      contactName: (formData.get("contact_name") || "").toString(),
      phone: (formData.get("phone") || "").toString(),
      hours: (formData.get("hours") || "").toString(),
      price: (formData.get("price") || "").toString(),
      facilities: (formData.get("facilities") || "").toString(),
      intro: (formData.get("intro") || "").toString()
    };
  }

  if (role === "coach") {
    return {
      ...base,
      name: (formData.get("name") || "").toString(),
      phone: (formData.get("phone") || "").toString(),
      specialties: (formData.get("specialties") || "").toString(),
      years: (formData.get("years") || "").toString(),
      price: (formData.get("price") || "").toString(),
      certifications: (formData.get("certifications") || "").toString(),
      intro: (formData.get("intro") || "").toString()
    };
  }

  return {
    ...base,
    name: (formData.get("name") || "").toString(),
    phone: (formData.get("phone") || "").toString(),
    gender: (formData.get("gender") || "").toString(),
    heightCm: (formData.get("height_cm") || "").toString(),
    weightKg: (formData.get("weight_kg") || "").toString(),
    level: (formData.get("level") || "").toString(),
    goal: (formData.get("goal") || "").toString(),
    intro: (formData.get("intro") || "").toString()
  };
}

function getThreadForProfile(profileId) {
  return state.threads.find((thread) => thread.withProfileId === profileId) || null;
}

function deepClone(value) {
  return value == null ? value : JSON.parse(JSON.stringify(value));
}

function showError(message) {
  window.alert(message || "操作失败，请稍后再试。");
}

async function runTask(task) {
  try {
    await task();
  } catch (error) {
    showError(error?.message || "操作失败，请稍后再试。");
  }
}

function renderAvatarMarkup(profile, className = "avatar") {
  const safeClassName = escapeHtml(className);
  const avatarAlt = escapeHtml(`${profile?.name || "用户"}头像`);
  const unreadCount = Math.max(0, Number(profile?.unreadCount || 0));
  const unreadBadge = unreadCount
    ? `<span class="avatar-unread-badge">${escapeHtml(unreadCount > 99 ? "99+" : String(unreadCount))}</span>`
    : "";
  const avatarSrc = profile?.avatarImage || createDefaultAvatar(profile?.role, profile?.name);

  return `
    <div class="${safeClassName} avatar--photo">
      <img class="avatar-image" src="${optimizeRemoteImageUrl(avatarSrc, "avatar")}" alt="${avatarAlt}" loading="lazy" decoding="async">
      ${unreadBadge}
    </div>
  `;
}

function toRadians(value) {
  return (value * Math.PI) / 180;
}

function getDistanceMeters(from, to) {
  const earthRadius = 6371000;
  const dLat = toRadians(to.lat - from.lat);
  const dLng = toRadians(to.lng - from.lng);
  const a =
    Math.sin(dLat / 2) * Math.sin(dLat / 2) +
    Math.cos(toRadians(from.lat)) *
      Math.cos(toRadians(to.lat)) *
      Math.sin(dLng / 2) *
      Math.sin(dLng / 2);
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
  return earthRadius * c;
}

function formatDistance(distance) {
  if (distance < 1000) return `${Math.round(distance)}m`;
  return `${(distance / 1000).toFixed(1)}km`;
}

function getRoleLabel(role) {
  return roleConfig[role]?.label || role;
}

function getRatingDisplay(profile) {
  if (!profile.ratingCount) return "新入驻";
  return profile.ratingAvg.toFixed(1);
}

function getProfile(profileId) {
  return state.profiles.find((profile) => profile.id === profileId) || null;
}

function updateProfile(profileId, updater) {
  const index = state.profiles.findIndex((profile) => profile.id === profileId);
  if (index === -1) return;
  const current = state.profiles[index];
  const next = typeof updater === "function" ? updater(current) : { ...current, ...updater };
  state.profiles[index] = next;
}

function getPostById(postId) {
  for (const profile of state.profiles) {
    const post = (profile.posts || []).find((item) => item.id === postId);
    if (post) {
      return { profile, post };
    }
  }
  const favoriteEntry = (state.favoritePosts || []).find((item) => item?.post?.id === postId || item?.id === postId);
  if (!favoriteEntry) return null;
  return favoriteEntry.post
    ? { profile: favoriteEntry.profile || null, post: favoriteEntry.post }
    : { profile: null, post: favoriteEntry };
}

function getPayloadPostById(payload, postId) {
  if (payload?.post?.id === postId) return payload.post;
  for (const profile of payload?.profiles || []) {
    const post = (profile.posts || []).find((item) => item.id === postId);
    if (post) return post;
  }
  const favoriteEntry = (payload?.favoritePosts || []).find((item) => item?.post?.id === postId || item?.id === postId);
  return favoriteEntry?.post || favoriteEntry || null;
}

function updatePostCollections(postId, updater) {
  state.profiles = state.profiles.map((profile) => {
    if (!Array.isArray(profile.posts) || !profile.posts.some((post) => post.id === postId)) return profile;
    return {
      ...profile,
      posts: profile.posts.map((post) => (post.id === postId ? updater({ ...post }) : post))
    };
  });

  if (Array.isArray(state.favoritePosts)) {
    state.favoritePosts = state.favoritePosts.map((entry) => {
      if (entry?.post?.id === postId) {
        return {
          ...entry,
          post: updater({ ...entry.post })
        };
      }
      if (entry?.id === postId) {
        return updater({ ...entry });
      }
      return entry;
    });
  }
}

function applyPostLikeState(postId, likedByCurrentActor, likeCount) {
  updatePostCollections(postId, (post) => ({
    ...post,
    likedByCurrentActor: Boolean(likedByCurrentActor),
    likeCount: Math.max(0, Number(likeCount || 0))
  }));
}

function refreshPostLikeButtons(postId) {
  const found = getPostById(postId);
  if (!found?.post) return;
  document.querySelectorAll("[data-like-post]").forEach((button) => {
    if (button.dataset.likePost !== postId) return;
    const liked = Boolean(found.post.likedByCurrentActor);
    button.classList.toggle("is-active", liked);
    button.setAttribute("aria-label", liked ? "取消点赞" : "点赞");
    const number = button.querySelector(".post-action-number");
    if (number) {
      number.textContent = String(found.post.likeCount || 0);
    }
  });
}

function getPostFavoriteDisplayCount(post) {
  const favoriteCount = Math.max(0, Number(post?.favoriteCount || 0));
  return state.favoritePostIds.has(post?.id) ? Math.max(1, favoriteCount) : favoriteCount;
}

function applyPostFavoriteState(postId, favorited) {
  const wasFavorited = state.favoritePostIds.has(postId);
  if (wasFavorited !== Boolean(favorited)) {
    updatePostCollections(postId, (post) => ({
      ...post,
      favoriteCount: Math.max(0, Number(post.favoriteCount || 0) + (favorited ? 1 : -1))
    }));
  }

  if (favorited) {
    state.favoritePostIds.add(postId);
    const hasEntry = (state.favoritePosts || []).some((item) => item?.post?.id === postId || item?.id === postId);
    const found = getAllPostEntries().find((item) => item.post?.id === postId);
    if (!hasEntry && found?.profile && found?.post) {
      state.favoritePosts = [
        {
          profile: found.profile,
          post: found.post,
          favoritedAt: new Date().toISOString()
        },
        ...(state.favoritePosts || [])
      ];
    }
    return;
  }

  state.favoritePostIds.delete(postId);
  state.favoritePosts = (state.favoritePosts || []).filter((item) => item?.post?.id !== postId && item?.id !== postId);
}

function insertOptimisticComment(postId, text) {
  const actor = getCurrentActor();
  const optimisticId = `optimistic-comment-${postId}-${Date.now()}-${Math.random().toString(16).slice(2)}`;
  const optimisticComment = {
    id: optimisticId,
    authorProfileId: actor?.id || "",
    authorName: actor?.name || "我",
    authorAvatarImage: actor?.avatarImage || "",
    text,
    createdAt: new Date().toISOString(),
    time: "刚刚",
    optimistic: true
  };

  updatePostCollections(postId, (post) => ({
    ...post,
    comments: [...(post.comments || []), optimisticComment]
  }));

  return optimisticId;
}

function removeOptimisticComment(postId, commentId) {
  updatePostCollections(postId, (post) => ({
    ...post,
    comments: (post.comments || []).filter((comment) => comment.id !== commentId)
  }));
}

function applyConfirmedPostState(postId, confirmedPost) {
  if (!confirmedPost) return;
  updatePostCollections(postId, (post) => ({
    ...post,
    ...confirmedPost
  }));
}

function refreshPostCommentViews(postId) {
  const found = getPostById(postId);
  if (!found?.post) return;
  document.querySelectorAll("[data-post-card]").forEach((card) => {
    if (card.dataset.postCard !== postId) return;
    const commentList = card.querySelector(".post-comment-list");
    if (commentList) {
      commentList.outerHTML = renderPostComments(found.post);
    }
    const count = card.querySelector(".post-action-button--count .post-action-number");
    if (count) {
      count.textContent = String(found.post.comments?.length || 0);
    }
    const input = card.querySelector(`[data-comment-input="${postId}"]`);
    if (input) {
      input.value = state.commentDrafts[postId] || "";
    }
  });
}

function refreshPostFavoriteButtons(postId) {
  const found = getPostById(postId);
  document.querySelectorAll("[data-favorite-post]").forEach((button) => {
    if (button.dataset.favoritePost !== postId) return;
    const favorited = state.favoritePostIds.has(postId);
    button.classList.toggle("is-active", favorited);
    button.setAttribute("aria-label", favorited ? "取消收藏" : "收藏");
    const number = button.querySelector(".post-action-number");
    if (number) {
      number.textContent = String(getPostFavoriteDisplayCount(found?.post));
    }
  });
}

async function flushPostLikeQueue(postId) {
  const mutation = state.likeMutationQueue.get(postId);
  if (!mutation || mutation.inFlight || mutation.queued <= 0) return;

  mutation.inFlight = true;
  mutation.queued -= 1;

  let failed = null;
  try {
    const payload = await postWithoutStateSync(`${API_BASE}/post/like`, { postId });
    const confirmed = getPayloadPostById(payload, postId);
    if (confirmed) {
      mutation.confirmedLiked = Boolean(confirmed.likedByCurrentActor);
      mutation.confirmedLikeCount = Number(confirmed.likeCount || 0);
    } else {
      mutation.confirmedLiked = !mutation.confirmedLiked;
      mutation.confirmedLikeCount = Math.max(
        0,
        Number(mutation.confirmedLikeCount || 0) + (mutation.confirmedLiked ? 1 : -1)
      );
    }
    if (mutation.queued > 0) {
      applyPostLikeState(postId, mutation.desiredLiked, mutation.desiredLikeCount);
    } else {
      applyPostLikeState(postId, mutation.confirmedLiked, mutation.confirmedLikeCount);
    }
  } catch (error) {
    failed = error;
  }

  mutation.inFlight = false;

  if (failed && mutation.queued <= 0) {
    applyPostLikeState(postId, mutation.confirmedLiked, mutation.confirmedLikeCount);
    state.likeMutationQueue.delete(postId);
    refreshPostLikeButtons(postId);
    showError(failed?.message || "点赞同步失败，请稍后再试。");
    return;
  }

  refreshPostLikeButtons(postId);

  if (mutation.queued > 0) {
    window.setTimeout(() => {
      flushPostLikeQueue(postId);
    }, 0);
    return;
  }

  state.likeMutationQueue.delete(postId);
  refreshPostLikeButtons(postId);
}

async function flushPostFavoriteQueue(postId) {
  const mutation = state.favoriteMutationQueue.get(postId);
  if (!mutation || mutation.inFlight || mutation.queued <= 0) return;

  mutation.inFlight = true;
  mutation.queued -= 1;

  let failed = null;
  try {
    const payload = await postWithoutStateSync(`${API_BASE}/post/favorite-toggle`, { postId });
    const confirmed = getPayloadPostById(payload, postId);
    mutation.confirmedFavorited = Array.isArray(payload?.favoritePostIds)
      ? payload.favoritePostIds.includes(postId)
      : !mutation.confirmedFavorited;
    if (confirmed) {
      updatePostCollections(postId, (post) => ({
        ...post,
        favoriteCount: Math.max(0, Number(confirmed.favoriteCount || 0))
      }));
    }
    if (mutation.queued > 0) {
      applyPostFavoriteState(postId, mutation.desiredFavorited);
    } else {
      applyPostFavoriteState(postId, mutation.confirmedFavorited);
    }
  } catch (error) {
    failed = error;
  }

  mutation.inFlight = false;

  if (failed && mutation.queued <= 0) {
    applyPostFavoriteState(postId, mutation.confirmedFavorited);
    state.favoriteMutationQueue.delete(postId);
    refreshPostFavoriteButtons(postId);
    showError(failed?.message || "收藏同步失败，请稍后再试。");
    return;
  }

  refreshPostFavoriteButtons(postId);

  if (mutation.queued > 0) {
    window.setTimeout(() => {
      flushPostFavoriteQueue(postId);
    }, 0);
    return;
  }

  state.favoriteMutationQueue.delete(postId);
  refreshPostFavoriteButtons(postId);
}

function insertOptimisticMessage(profileId, text) {
  const actor = getCurrentActor();
  const targetProfile = getProfile(profileId);
  const optimisticId = `optimistic-${profileId}-${Date.now()}`;
  const createdAt = new Date().toISOString();
  const optimisticMessage = {
    id: optimisticId,
    senderProfileId: actor?.id || "",
    senderName: actor?.name || "我",
    text,
    createdAt,
    time: "刚刚",
    optimistic: true
  };

  const threadIndex = state.threads.findIndex((thread) => thread.withProfileId === profileId);
  if (threadIndex >= 0) {
    const thread = state.threads[threadIndex];
    state.threads[threadIndex] = {
      ...thread,
      messages: [...(thread.messages || []), optimisticMessage],
      lastMessage: { text, time: "刚刚" }
    };
  } else {
    state.threads = [
      {
        id: `optimistic-thread-${profileId}`,
        withProfileId: profileId,
        withProfileName: targetProfile?.name || "聊天对象",
        withProfileAvatarImage: targetProfile?.avatarImage || "",
        messages: [optimisticMessage],
        lastMessage: { text, time: "刚刚" }
      },
      ...state.threads
    ];
  }

  return optimisticId;
}

function mergeConfirmedThread(profileId, confirmedThread, optimisticMessageId) {
  if (!confirmedThread) return;
  const localThread = getThreadForProfile(profileId);
  const remainingOptimisticMessages = (localThread?.messages || []).filter(
    (message) => message.optimistic && message.id !== optimisticMessageId
  );
  const confirmedMessages = confirmedThread.messages || [];
  const mergedMessages = [...confirmedMessages, ...remainingOptimisticMessages].sort((left, right) =>
    String(left.createdAt || "").localeCompare(String(right.createdAt || ""))
  );
  const lastMessage = mergedMessages[mergedMessages.length - 1] || confirmedThread.lastMessage || null;
  const nextThread = {
    ...confirmedThread,
    messages: mergedMessages,
    lastMessage
  };
  const existingIndex = state.threads.findIndex((thread) => thread.withProfileId === profileId || thread.id === confirmedThread.id);
  if (existingIndex >= 0) {
    state.threads[existingIndex] = nextThread;
  } else {
    state.threads = [nextThread, ...(state.threads || [])];
  }
  state.threads = [...state.threads].sort((left, right) =>
    String(right.lastMessage?.createdAt || "").localeCompare(String(left.lastMessage?.createdAt || ""))
  );
}

function removeOptimisticMessage(profileId, messageId) {
  state.threads = (state.threads || [])
    .map((thread) => {
      if (thread.withProfileId !== profileId) return thread;
      const nextMessages = (thread.messages || []).filter((message) => message.id !== messageId);
      return {
        ...thread,
        messages: nextMessages,
        lastMessage: nextMessages.length
          ? {
              text: nextMessages[nextMessages.length - 1]?.text || "打开查看最新消息",
              time: nextMessages[nextMessages.length - 1]?.time || "刚刚"
            }
          : thread.id.startsWith("optimistic-thread-")
            ? null
            : thread.lastMessage
      };
    })
    .filter((thread) => (thread.messages || []).length || !String(thread.id || "").startsWith("optimistic-thread-"));
}

function getManagedProfiles() {
  return state.managedProfileIds.map(getProfile).filter(Boolean);
}

function getManagedProfileByRole(role) {
  return getManagedProfiles().find((profile) => profile.role === role) || null;
}

function hasManagedRole(role) {
  return Boolean(getManagedProfileByRole(role));
}

function getCurrentActor() {
  return getProfile(state.currentActorProfileId) || getManagedProfiles()[0] || null;
}

function getMyPageProfile() {
  return getManagedProfileByRole(state.selectedRole) || getCurrentActor() || getManagedProfiles()[0] || null;
}

function renderCardCover(profile) {
  const coverImage = getProfileCoverImage(profile);
  if (!coverImage) {
    return `<div class="card-cover ${profile.role} image-shell image-shell--cover"></div>`;
  }
  return `
    <div class="card-cover ${profile.role} image-shell image-shell--cover">
      <img class="card-cover-image" src="${optimizeRemoteImageUrl(coverImage, "cover")}" alt="${escapeHtml(profile.name || "封面图")}" loading="lazy" decoding="async">
      <span class="card-cover-overlay"></span>
    </div>
  `;
}

function getHomeProfiles(role) {
  const keyword = state.searchKeyword.trim().toLowerCase();
  return state.profiles
    .filter((profile) => profile.role === role && profile.listed)
    .map((profile) => ({
      ...profile,
      distanceMeters: getDistanceMeters(state.userPosition, {
        lat: profile.lat,
        lng: profile.lng
      })
    }))
    .filter((profile) => {
      if (!keyword) return true;
      return `${profile.name}${profile.bio}${profile.shortDesc}${profile.price}${profile.tags.join("")}`
        .toLowerCase()
        .includes(keyword);
    })
    .sort((left, right) => left.distanceMeters - right.distanceMeters);
}

function getDiscoverProfiles() {
  const actor = getCurrentActor();
  return state.profiles
    .filter((profile) => profile.id !== actor?.id)
    .sort((left, right) => right.followers - left.followers)
    .slice(0, 6);
}

function getLocationDistrictLabel(profile) {
  const raw = String(profile?.locationLabel || profile?.location || "").trim();
  if (!raw) return "";
  const segments = raw.split("·").map((item) => item.trim()).filter(Boolean);
  return segments[1] || segments[0] || "";
}

function buildRecommendedCandidate(profile) {
  const distanceMeters = getDistanceMeters(state.userPosition, {
    lat: profile.lat,
    lng: profile.lng
  });
  const district = getLocationDistrictLabel(profile);
  const currentDistrict = String(state.userPosition.district || "").trim();
  const sameDistrict = Boolean(district && currentDistrict && district.includes(currentDistrict));
  const sameCity = profile.city === state.userPosition.city;
  return {
    ...profile,
    distanceMeters,
    sameCity,
    sameDistrict
  };
}

function getRelativeMinutes(label = "") {
  const value = String(label).trim();
  if (!value) return 12 * 60;
  if (value.includes("刚刚")) return 0;
  if (value.includes("稍后")) return 5;

  let match = value.match(/(\d+)\s*分钟前/);
  if (match) return Number(match[1]);

  match = value.match(/(\d+)\s*小时前/);
  if (match) return Number(match[1]) * 60;

  match = value.match(/(\d+)\s*天前/);
  if (match) return Number(match[1]) * 24 * 60;

  if (value.includes("今天")) return 3 * 60;
  if (value.includes("昨天")) return 24 * 60;
  return 12 * 60;
}

function getRecommendedProfiles() {
  const actor = getCurrentActor();
  const candidates = state.profiles
    .filter(
      (profile) =>
        profile.id !== actor?.id &&
        profile.listed &&
        !state.followSet.has(profile.id)
    )
    .map((profile) => buildRecommendedCandidate(profile));

  if (!candidates.length) return [];

  const used = new Set();
  const recommendations = [];
  const targetCount = candidates.length <= 15 ? candidates.length : 12;

  function addFromPool(pool, limit, reasonLabel, detailFormatter) {
    for (const profile of pool) {
      if (recommendations.length >= targetCount || limit <= 0) break;
      if (used.has(profile.id)) continue;
      used.add(profile.id);
      recommendations.push({
        ...profile,
        recommendReason: reasonLabel,
        recommendDetail: detailFormatter(profile)
      });
      limit -= 1;
    }
  }

  const nearbyPool = [...candidates]
    .filter((profile) => profile.sameCity || profile.distanceMeters <= 12000)
    .sort((left, right) => {
      if (right.sameDistrict !== left.sameDistrict) return Number(right.sameDistrict) - Number(left.sameDistrict);
      if (right.sameCity !== left.sameCity) return Number(right.sameCity) - Number(left.sameCity);
      if (left.distanceMeters !== right.distanceMeters) return left.distanceMeters - right.distanceMeters;
      if (right.followers !== left.followers) return right.followers - left.followers;
      return right.ratingAvg - left.ratingAvg;
    });

  const followersPool = [...candidates].sort((left, right) => {
    if (right.followers !== left.followers) return right.followers - left.followers;
    if (right.ratingAvg !== left.ratingAvg) return right.ratingAvg - left.ratingAvg;
    return left.distanceMeters - right.distanceMeters;
  });

  const ratingPool = [...candidates]
    .filter((profile) => Number(profile.ratingCount || 0) > 0)
    .sort((left, right) => {
      if (right.ratingAvg !== left.ratingAvg) return right.ratingAvg - left.ratingAvg;
      if (right.ratingCount !== left.ratingCount) return right.ratingCount - left.ratingCount;
      if (right.followers !== left.followers) return right.followers - left.followers;
      return left.distanceMeters - right.distanceMeters;
    });

  addFromPool(
    nearbyPool,
    Math.min(5, targetCount),
    "可能认识",
    (profile) =>
      `${profile.sameDistrict ? "同片区" : profile.sameCity ? "同城附近" : "附近用户"} · ${formatDistance(profile.distanceMeters)}`
  );
  addFromPool(
    followersPool,
    Math.min(4, targetCount - recommendations.length),
    "粉丝较多",
    (profile) => `${profile.followers || 0} 粉丝`
  );
  addFromPool(
    ratingPool,
    Math.min(4, targetCount - recommendations.length),
    "评分较高",
    (profile) => `${Number(profile.ratingAvg || 0).toFixed(1)} 分 · ${profile.ratingCount || 0} 条评分`
  );

  const fallbackPool = [...candidates].sort((left, right) => {
    if (right.sameCity !== left.sameCity) return Number(right.sameCity) - Number(left.sameCity);
    if (right.followers !== left.followers) return right.followers - left.followers;
    if (right.ratingAvg !== left.ratingAvg) return right.ratingAvg - left.ratingAvg;
    return left.distanceMeters - right.distanceMeters;
  });

  addFromPool(
    fallbackPool,
    targetCount - recommendations.length,
    "值得关注",
    (profile) =>
      profile.sameCity ? `${profile.city || "同城"} · ${formatDistance(profile.distanceMeters)}` : `${profile.city || "附近"}`
  );

  return recommendations;
}

function getFollowedProfiles() {
  const actor = getCurrentActor();
  return state.profiles
    .filter(
      (profile) =>
        profile.listed &&
        profile.id !== actor?.id &&
        state.followSet.has(profile.id)
    )
    .sort((left, right) => {
      if (right.followers !== left.followers) return right.followers - left.followers;
      if (right.ratingAvg !== left.ratingAvg) return right.ratingAvg - left.ratingAvg;
      return String(left.name).localeCompare(String(right.name), "zh-Hans-CN");
    });
}

function getFollowerProfiles() {
  const actor = getCurrentActor();
  return state.profiles
    .filter(
      (profile) =>
        profile.listed &&
        profile.id !== actor?.id &&
        state.followerSet.has(profile.id)
    )
    .sort((left, right) => {
      if (right.followers !== left.followers) return right.followers - left.followers;
      if (right.ratingAvg !== left.ratingAvg) return right.ratingAvg - left.ratingAvg;
      return String(left.name).localeCompare(String(right.name), "zh-Hans-CN");
    });
}

function isMediaPost(post) {
  return Boolean(Array.isArray(post?.media) && post.media.some((item) => item?.url));
}

function getAllPostEntries() {
  return state.profiles
    .flatMap((profile) => (profile.posts || []).map((post) => ({ profile, post })))
    .sort((left, right) => String(right.post?.createdAt || "").localeCompare(String(left.post?.createdAt || "")));
}

function getFavoritedMediaEntries() {
  const savedEntries = Array.isArray(state.favoritePosts)
    ? state.favoritePosts
        .filter((item) => item?.profile && item?.post && isMediaPost(item.post))
        .map((item) => ({ profile: item.profile, post: item.post }))
    : [];

  const seenPostIds = new Set(savedEntries.map((item) => item.post.id));
  getAllPostEntries().forEach((item) => {
    if (!isMediaPost(item.post) || seenPostIds.has(item.post.id) || !state.favoritePostIds.has(item.post.id)) {
      return;
    }
    savedEntries.push(item);
    seenPostIds.add(item.post.id);
  });

  return savedEntries.sort((left, right) => String(right.post?.createdAt || "").localeCompare(String(left.post?.createdAt || "")));
}

function getInboxCount() {
  return getTotalUnreadInboxCount();
}

function getBookingsForProfile(profile, direction = "") {
  if (!profile?.id) return [];
  const items = (state.bookings || []).filter((item) => {
    const matchesIncoming = item.targetProfileId === profile.id || (item.direction === "incoming" && item.targetProfileId === profile.id);
    const matchesOutgoing = item.createdByProfileId === profile.id || (item.direction === "outgoing" && item.createdByProfileId === profile.id);
    if (direction === "incoming") return matchesIncoming;
    if (direction === "outgoing") return matchesOutgoing;
    return matchesIncoming || matchesOutgoing;
  });
  return [...items].sort(
    (left, right) => new Date(right.createdAt || 0).getTime() - new Date(left.createdAt || 0).getTime()
  );
}

function getRelevantBookingsForProfile(profile) {
  if (!profile) return [];
  return profile.role === "enthusiast"
    ? getBookingsForProfile(profile, "outgoing")
    : getBookingsForProfile(profile, "incoming");
}

function getIncomingBookings(profile) {
  return getBookingsForProfile(profile, "incoming");
}

function getOutgoingBookings(profile) {
  return getBookingsForProfile(profile, "outgoing");
}

function getFollowingFeedItems() {
  const actor = getCurrentActor();
  return state.profiles
    .filter(
      (profile) =>
        profile.listed &&
        profile.id !== actor?.id &&
        state.followSet.has(profile.id)
    )
    .flatMap((profile) => {
      const posts = Array.isArray(profile.posts) ? profile.posts : [];
      if (posts.length) {
        return posts.map((post, index) => ({
          id: `${profile.id}-post-${index}`,
          kind: "post",
          profile,
          post,
          minutes: getTimelineMinutes(post.createdAt, post.time)
        }));
      }

      return [
        {
          id: `${profile.id}-intro`,
          kind: "profile",
          profile,
          minutes: getTimelineMinutes(profile.createdAt, "最近")
        }
      ];
    })
    .sort((left, right) => {
      if (left.minutes !== right.minutes) return left.minutes - right.minutes;
      return right.profile.followers - left.profile.followers;
    })
    .slice(0, 10);
}

function getTimelineMinutes(createdAt = "", fallbackLabel = "") {
  const created = createdAt ? new Date(createdAt).getTime() : NaN;
  if (Number.isFinite(created) && created > 0) {
    return Math.max(0, Math.round((Date.now() - created) / 60000));
  }
  return getRelativeMinutes(fallbackLabel);
}

function renderDiscoverProfileEntry(profile) {
  return `
    <article class="timeline-card timeline-card--compact">
      <div class="timeline-head">
        <div class="timeline-author">
          ${renderAvatarMarkup(profile, "avatar")}
          <div>
            <strong>${escapeHtml(profile.name)}</strong>
            <p>${escapeHtml(profile.handle)} · ${escapeHtml(getRoleLabel(profile.role))}</p>
          </div>
        </div>
        <span>已关注</span>
      </div>
      <p>${escapeHtml(profile.bio || profile.shortDesc || "这个用户刚刚加入了 FitHub。")}</p>
      <small>${escapeHtml(profile.locationLabel || profile.city || "同城用户")}</small>
      <div class="post-action-bar">
        <button class="mini-button" data-open-profile="${profile.id}" type="button">查看主页</button>
      </div>
    </article>
  `;
}

function slugForRole(role) {
  return `${role}_${String(Date.now()).slice(-4)}`;
}

function getInitialCharacter(name) {
  return Array.from(name || "?")[0] || "?";
}

function syncNavActive() {
  navLinks.forEach((link) => {
    link.classList.toggle("is-active", link.dataset.page === state.activePage);
  });
}

function openOverlay(mode) {
  state.overlayMode = mode;
  state.registerSuccess = "";
  renderOverlay();
}

function closeOverlay() {
  if (state.overlayMode === "compose" && state.composeMedia.length) {
    const draftMedia = [...state.composeMedia];
    runTask(() => cleanupComposeDraftMedia(draftMedia));
    state.composeMedia = [];
  }
  if (state.overlayMode === "register") {
    state.registerUploadDrafts = {};
    state.registerFormDrafts = {};
    state.registerWheelField = "";
  }
  if (state.overlayMode === "media") {
    state.mediaViewerPostId = "";
    state.mediaViewerIndex = 0;
  }
  state.overlayMode = null;
  state.registerSuccess = "";
  state.authMessage = "";
  renderOverlay();
}

function openRegister(role = state.selectedRole) {
  state.registerRole = role;
  state.selectedRole = role;
  state.overlayReturnMode = null;
  state.registerUploadDrafts = {};
  state.registerFormDrafts = {};
  state.registerCodeCooldownUntil = 0;
  state.registerWheelField = "";
  seedRegisterDraft(role);
  openOverlay("register");
}

function openAuth(role = state.selectedRole) {
  const remembered = getPreferredStoredAccount(role);
  state.authRole = role;
  state.authPhone = remembered?.phone || "";
  state.authAccountId = remembered?.id || "";
  state.authRestoreToken = remembered?.restoreToken || "";
  state.authVerificationCode = "";
  state.authCodeCooldownUntil = 0;
  state.authCodeHint = "";
  state.authMessage = "";
  state.authMatches = [];
  openOverlay("auth");
}

function openMyPage() {
  const myProfile = getMyPageProfile();
  if (state.activePage !== "profile") {
    state.profileReturnPage = state.activePage;
  }
  state.activePage = "profile";
  state.activeProfileId = myProfile?.id || state.currentActorProfileId || "";
  state.profileSubpage = "";
  state.outdoorShareCheckinId = "";
  syncNavActive();
  renderPage();
  appView.scrollTop = 0;
}

function openComposer() {
  const managedProfiles = getManagedProfiles();
  if (!managedProfiles.length) {
    openOverlay("welcome");
    return;
  }
  state.composeProfileId = state.currentActorProfileId || managedProfiles[0].id;
  state.composeContent = "";
  state.composeMeta = "";
  state.composeMedia = [];
  openOverlay("compose");
}

function openCitySelector(returnMode = null) {
  state.cityInput = state.userPosition.city || "";
  state.overlayReturnMode = returnMode;
  openOverlay("city");
}

async function persistLocationState(keepOverlay = false) {
  await postAndSync(`${API_BASE}/session/location`, {
    userPosition: state.userPosition,
    locationStatus: state.locationStatus
  }, { keepOverlay });
}

async function applyPresetCity(key) {
  const preset = CITY_PRESETS[key];
  if (!preset) return;
  state.userPosition = {
    ...preset,
    source: "preset"
  };
  state.locationStatus = `已切换到 ${preset.label}，附近健身房、教练和注册表单都会基于这个城市展示。`;
  state.searchKeyword = "";
  if (state.overlayReturnMode) {
    const mode = state.overlayReturnMode;
    state.overlayReturnMode = null;
    state.overlayMode = mode;
  } else {
    closeOverlay();
  }
  await persistLocationState(Boolean(state.overlayMode));
  renderPage();
}

async function applyManualCity() {
  const cityName = state.cityInput.trim();
  if (!cityName) return;
  const matched = Object.values(CITY_PRESETS).find((preset) => cityName.includes(preset.city));
  if (matched) {
    await applyPresetCity(matched.key);
    return;
  }

  state.userPosition = {
    ...state.userPosition,
    city: cityName,
    district: "",
    label: `${cityName} · 手动选择`,
    source: "manual"
  };
  state.locationStatus = `已手动切换到 ${cityName}。正式版接入地图编码后，可自动换算附近距离。`;
  if (state.overlayReturnMode) {
    const mode = state.overlayReturnMode;
    state.overlayReturnMode = null;
    state.overlayMode = mode;
  } else {
    closeOverlay();
  }
  await persistLocationState(Boolean(state.overlayMode));
  renderPage();
}

function resolveDemoCity(latitude, longitude) {
  const nearest = Object.values(CITY_PRESETS)
    .map((preset) => ({
      preset,
      distance: getDistanceMeters(
        { lat: latitude, lng: longitude },
        { lat: preset.lat, lng: preset.lng }
      )
    }))
    .sort((left, right) => left.distance - right.distance)[0];

  if (nearest && nearest.distance < 30000) {
    return nearest.preset;
  }

  return {
    key: "live",
    city: "我的城市",
    district: "实时定位",
    label: "我的城市 · 实时定位",
    lat: latitude,
    lng: longitude
  };
}

function requestCurrentLocation() {
  state.locationStatus = "正在获取你的实时定位...";
  renderPage();
  renderOverlay();

  if (!navigator.geolocation) {
    state.locationStatus = "当前浏览器不支持定位，请切换城市或在注册时手动填写地址。";
    renderPage();
    renderOverlay();
    return;
  }

  navigator.geolocation.getCurrentPosition(
    (position) => {
      const { latitude, longitude } = position.coords;
      const resolved = resolveDemoCity(latitude, longitude);
      state.userPosition = {
        ...resolved,
        lat: latitude,
        lng: longitude,
        source: "live"
      };
      state.locationStatus = `已同步实时定位：${resolved.label}。正式版会配合地图 SDK 自动反查城市和街道。`;
      if (state.overlayReturnMode) {
        const mode = state.overlayReturnMode;
        state.overlayReturnMode = null;
        state.overlayMode = mode;
      } else {
        closeOverlay();
      }
      runTask(async () => {
        await persistLocationState(Boolean(state.overlayMode));
        renderPage();
      });
    },
    () => {
      state.locationStatus = "定位失败，请检查浏览器权限；你也可以手动选择城市。";
      renderPage();
      renderOverlay();
    },
    { enableHighAccuracy: true, timeout: 10000, maximumAge: 300000 }
  );
}

function isManagedProfile(profileId) {
  return state.managedProfileIds.includes(profileId);
}

async function toggleFollow(profileId) {
  if (isManagedProfile(profileId)) return;
  await postAndSync(`${API_BASE}/follow/toggle`, {
    targetProfileId: profileId
  });
  renderPage();
}

function openProfile(profileId) {
  if (state.profileSubpage) {
    state.profileReturnPage = "my";
  } else if (state.activePage !== "profile") {
    state.profileReturnPage = state.activePage;
  }
  state.profileSubpage = "";
  state.activeProfileId = profileId;
  state.activePage = "profile";
  syncNavActive();
  renderPage();
  appView.scrollTop = 0;
}

function getProfileReturnLabel() {
  if (state.profileSubpage) return "我的";
  if (state.profileReturnPage === "my") return "我的";
  if (state.profileReturnPage === "discover") return "探索";
  if (state.profileReturnPage === "booking") return "预约";
  return "首页";
}

function goBackFromProfile() {
  if (state.profileSubpage) {
    state.profileSubpage = "";
    renderPage();
    appView.scrollTop = 0;
    return;
  }
  if (state.profileReturnPage === "my") {
    state.profileReturnPage = "home";
    openMyPage();
    return;
  }
  state.activePage =
    state.profileReturnPage && state.profileReturnPage !== "profile"
      ? state.profileReturnPage
      : "home";
  state.profileReturnPage = "home";
  syncNavActive();
  renderPage();
  appView.scrollTop = 0;
}

function clearProfileSwipeStyles() {
  appView.classList.remove("is-swipe-preview");
  appView.style.transform = "";
  appView.style.transition = "";
}

function resetProfileSwipe() {
  profileSwipe.active = false;
  profileSwipe.engaged = false;
  profileSwipe.pointerId = null;
  profileSwipe.startX = 0;
  profileSwipe.startY = 0;
  profileSwipe.offset = 0;
  clearProfileSwipeStyles();
}

function getRegistrationSeed(role) {
  return getManagedProfiles().find((profile) => profile.role === role) || {};
}

function getRegisterWheelConfig(fieldName) {
  return REGISTER_WHEEL_FIELDS[fieldName] || null;
}

function formatRegisterWheelNumber(value) {
  const numeric = Number(value);
  if (!Number.isFinite(numeric)) return "";
  if (Math.abs(numeric - Math.round(numeric)) < 0.001) return String(Math.round(numeric));
  return numeric.toFixed(1).replace(/\.0$/, "");
}

function getRegisterDraft(role = state.registerRole) {
  if (!state.registerFormDrafts[role]) {
    state.registerFormDrafts[role] = {};
  }
  return state.registerFormDrafts[role];
}

function setRegisterDraftValue(role, fieldName, value) {
  const draft = getRegisterDraft(role);
  draft[fieldName] = value == null ? "" : String(value);
}

function getFieldDefault(field, seed) {
  if (field.name === "city") return seed.city || state.userPosition.city;
  if (field.name === "location") return seed.locationLabel || state.userPosition.label;
  if (field.name === "gym_name") return seed.name || "";
  if (field.name === "name") return seed.name || "";
  if (field.name === "price") return seed.price || "";
  if (field.name === "intro") return seed.bio || "";
  if (field.name === "facilities") return (seed.tags || []).join("、");
  if (field.name === "specialties") return (seed.tags || []).join("、");
  if (field.name === "years") return seed.years || "";
  if (field.name === "certifications") return (seed.certifications || []).join("、");
  if (field.name === "goal") return seed.goal || "";
  if (field.name === "level") return seed.level || "";
  if (field.name === "gender") return seed.gender || "";
  if (field.name === "height_cm") return seed.heightCm || "";
  if (field.name === "weight_kg") return seed.weightKg || "";
  return seed[field.name] || "";
}

function seedRegisterDraft(role = state.registerRole) {
  const seed = getRegistrationSeed(role);
  const draft = getRegisterDraft(role);

  roleConfig[role].fields.forEach((field) => {
    if (Object.prototype.hasOwnProperty.call(draft, field.name) && draft[field.name] !== "") return;
    let value = getFieldDefault(field, seed);
    const wheelConfig = getRegisterWheelConfig(field.name);
    if ((value === "" || value == null) && wheelConfig) {
      value = wheelConfig.defaultValue;
    }
    draft[field.name] = value == null ? "" : String(value);
  });

  return draft;
}

function getRegisterFieldValue(field, seed, role = state.registerRole) {
  const draft = getRegisterDraft(role);
  if (Object.prototype.hasOwnProperty.call(draft, field.name)) {
    return draft[field.name];
  }
  let value = getFieldDefault(field, seed);
  const wheelConfig = getRegisterWheelConfig(field.name);
  if ((value === "" || value == null) && wheelConfig) {
    value = wheelConfig.defaultValue;
  }
  return value == null ? "" : String(value);
}

function getRegisterWheelOptions(fieldName) {
  const config = getRegisterWheelConfig(fieldName);
  if (!config) return [];

  const options = [];
  const precision = config.step < 1 ? 10 : 1;
  for (let current = config.min * precision; current <= config.max * precision; current += config.step * precision) {
    options.push(formatRegisterWheelNumber(current / precision));
  }
  return options;
}

function getRegisterWheelValue(fieldName) {
  const config = getRegisterWheelConfig(fieldName);
  const value = getRegisterFieldValue({ name: fieldName }, getRegistrationSeed(state.registerRole));
  if (value !== "") return String(value);
  return config ? formatRegisterWheelNumber(config.defaultValue) : "";
}

function formatRegisterWheelDisplay(fieldName, value) {
  const config = getRegisterWheelConfig(fieldName);
  if (!config || value === "" || value == null) return "未设置";
  return `${formatRegisterWheelNumber(value)} ${config.unit}`;
}

function syncRegisterWheelDom(fieldName) {
  const selectedValue = getRegisterWheelValue(fieldName);
  overlay
    .querySelectorAll(`[data-register-wheel-option="${fieldName}"]`)
    .forEach((option) => {
      const active = option.dataset.wheelValue === selectedValue;
      option.classList.toggle("is-active", active);
      option.setAttribute("aria-selected", active ? "true" : "false");
    });

  const summary = overlay.querySelector("[data-register-wheel-value]");
  if (summary) {
    summary.textContent = formatRegisterWheelDisplay(fieldName, selectedValue);
  }

  const hiddenInput = overlay.querySelector(`input[name="${fieldName}"]`);
  if (hiddenInput) {
    hiddenInput.value = selectedValue;
  }
}

function scrollRegisterWheelToValue(fieldName, behavior = "smooth") {
  const list = overlay.querySelector(`[data-register-wheel-list="${fieldName}"]`);
  if (!list) return;
  const optionNodes = Array.from(list.querySelectorAll(`[data-register-wheel-option="${fieldName}"]`));
  const selectedValue = getRegisterWheelValue(fieldName);
  const index = optionNodes.findIndex((option) => option.dataset.wheelValue === selectedValue);
  if (index === -1) return;
  list.scrollTo({ top: index * REGISTER_WHEEL_ITEM_HEIGHT, behavior });
}

function initializeRegisterWheelPicker() {
  const fieldName = state.registerWheelField;
  if (!fieldName) return;

  const list = overlay.querySelector(`[data-register-wheel-list="${fieldName}"]`);
  if (!list || list.dataset.ready === "1") {
    syncRegisterWheelDom(fieldName);
    return;
  }

  list.dataset.ready = "1";
  syncRegisterWheelDom(fieldName);

  requestAnimationFrame(() => {
    scrollRegisterWheelToValue(fieldName, "auto");
  });

  let frame = 0;
  list.addEventListener(
    "scroll",
    () => {
      cancelAnimationFrame(frame);
      frame = requestAnimationFrame(() => {
        const optionNodes = Array.from(list.querySelectorAll(`[data-register-wheel-option="${fieldName}"]`));
        if (!optionNodes.length) return;
        const index = Math.max(0, Math.min(optionNodes.length - 1, Math.round(list.scrollTop / REGISTER_WHEEL_ITEM_HEIGHT)));
        const value = optionNodes[index].dataset.wheelValue;
        setRegisterDraftValue(state.registerRole, fieldName, value);
        syncRegisterWheelDom(fieldName);
      });
    },
    { passive: true }
  );
}

function renderRegisterWheelSheet() {
  const fieldName = state.registerWheelField;
  const config = getRegisterWheelConfig(fieldName);
  if (!config) return "";

  const options = getRegisterWheelOptions(fieldName);
  const selectedValue = getRegisterWheelValue(fieldName);

  return `
    <div class="register-wheel-sheet">
      <button class="register-wheel-backdrop" data-close-register-wheel="1" type="button" aria-label="关闭选择器"></button>
      <div class="register-wheel-card">
        <div class="sport-picker-handle"></div>
        <div class="register-wheel-head">
          <div>
            <p class="page-label">滚轮选择</p>
            <h3>${config.label}</h3>
          </div>
          <button class="mini-button mini-button--accent" data-confirm-register-wheel="1" type="button">完成</button>
        </div>
        <div class="register-wheel-summary">
          <strong data-register-wheel-value="1">${escapeHtml(formatRegisterWheelDisplay(fieldName, selectedValue))}</strong>
          <span>${escapeHtml(config.helper)}</span>
        </div>
        <div class="register-wheel-frame">
          <div class="register-wheel-highlight" aria-hidden="true"></div>
          <div class="register-wheel-list" data-register-wheel-list="${fieldName}" role="listbox" aria-label="${escapeHtml(config.label)}选择">
            ${options
              .map(
                (option) => `
                  <button
                    class="register-wheel-option ${option === selectedValue ? "is-active" : ""}"
                    data-register-wheel-option="${fieldName}"
                    data-wheel-value="${escapeHtml(option)}"
                    type="button"
                    role="option"
                    aria-selected="${option === selectedValue ? "true" : "false"}"
                  >
                    <span>${escapeHtml(option)}</span>
                    <small>${escapeHtml(config.unit)}</small>
                  </button>
                `
              )
              .join("")}
          </div>
        </div>
      </div>
    </div>
  `;
}

function renderField(field, seed) {
  const value = getRegisterFieldValue(field, seed);

  if (field.type === "textarea") {
    return `
      <label class="form-field">
        <span>${field.label}${field.required ? " *" : ""}</span>
        <textarea name="${field.name}" placeholder="${escapeHtml(field.placeholder || "")}" ${field.required ? "required" : ""}>${escapeHtml(value)}</textarea>
      </label>
    `;
  }

  if (field.type === "select") {
    return `
      <label class="form-field">
        <span>${field.label}${field.required ? " *" : ""}</span>
        <select name="${field.name}" ${field.required ? "required" : ""}>
          <option value="">请选择</option>
          ${field.options
            .map(
              (option) => `
                <option value="${escapeHtml(option)}" ${option === value ? "selected" : ""}>${escapeHtml(option)}</option>
              `
            )
            .join("")}
        </select>
      </label>
    `;
  }

  if (field.type === "file") {
    const isAvatarField = field.name === "avatar_file";
    const uploadDraft = state.registerUploadDrafts[field.name];
    const currentPreview = uploadDraft?.preview || (isAvatarField ? seed.avatarImage : "");
    const currentLabel = uploadDraft?.label || (currentPreview ? "已选择文件" : field.multiple ? "可选，多张上传" : "可选，轻触上传");
    return `
      <div class="form-field">
        <span>${field.label}${field.required ? " *" : "（可选）"}</span>
        <label class="upload-picker ${currentPreview ? "has-preview" : ""}">
          <input
            class="upload-picker-input"
            name="${field.name}"
            type="file"
            ${field.accept ? `accept="${field.accept}"` : ""}
            ${field.multiple ? "multiple" : ""}
          >
          <div class="upload-picker-copy">
            <strong>${isAvatarField ? "上传头像" : field.multiple ? "上传资料图片" : "上传文件"}</strong>
            <p>${currentLabel}</p>
          </div>
          ${
            currentPreview
              ? `
                <div class="upload-picker-preview">
                  ${
                    isAvatarField
                      ? renderAvatarMarkup({ ...seed, avatarImage: currentPreview }, "avatar avatar--register-preview")
                      : `<img src="${currentPreview}" alt="${escapeHtml(field.label)}预览">`
                  }
                </div>
              `
              : '<div class="upload-picker-mark">+</div>'
          }
        </label>
      </div>
    `;
  }

  if (getRegisterWheelConfig(field.name)) {
    const wheelConfig = getRegisterWheelConfig(field.name);
    return `
      <label class="form-field form-field--wheel">
        <span>${field.label}${field.required ? " *" : ""}</span>
        <button class="wheel-trigger" data-open-register-wheel="${field.name}" type="button">
          <div class="wheel-trigger-copy">
            <strong>${escapeHtml(formatRegisterWheelDisplay(field.name, value))}</strong>
            <small>${escapeHtml(wheelConfig.helper)}</small>
          </div>
          <span class="wheel-trigger-mark">${escapeHtml(wheelConfig.unit)}</span>
        </button>
        <input name="${field.name}" type="hidden" value="${escapeHtml(value)}">
      </label>
    `;
  }

  return `
    <label class="form-field">
      <span>${field.label}${field.required ? " *" : ""}</span>
      <input
        name="${field.name}"
        type="${field.type}"
        value="${escapeHtml(value)}"
        placeholder="${escapeHtml(field.placeholder || "")}"
        ${field.required ? "required" : ""}
      >
    </label>
  `;
}

function renderAuthVerificationField() {
  if (!isSmsVerificationEnabled()) return "";
  const secondsLeft = Math.max(0, Math.ceil((state.authCodeCooldownUntil - Date.now()) / 1000));
  return `
    <div class="form-field">
      <span>短信验证码 *</span>
      <div class="verification-row">
        <input
          data-auth-code="1"
          name="verification_code"
          type="tel"
          inputmode="numeric"
          maxlength="6"
          value="${escapeHtml(state.authVerificationCode)}"
          placeholder="请输入短信验证码"
          required
        >
        <button
          class="mini-button ${secondsLeft ? "" : "mini-button--accent"}"
          data-send-auth-code="1"
          type="button"
          ${secondsLeft ? "disabled" : ""}
        >${secondsLeft ? escapeHtml(getSmsSendCooldown(secondsLeft)) : "发送验证码"}</button>
      </div>
      <small class="helper-note">${escapeHtml(state.authCodeHint || "换设备登录时使用短信验证码，同设备已登录会自动恢复。")}</small>
    </div>
  `;
}

function renderRegisterVerificationField() {
  if (!isSmsVerificationEnabled()) return "";
  const secondsLeft = Math.max(0, Math.ceil((state.registerCodeCooldownUntil - Date.now()) / 1000));
  const helperText = state.registerSuccess || state.authCodeHint || "新设备注册或绑定手机号时，用验证码确认本人操作。";
  return `
    <label class="form-field">
      <span>短信验证码 *</span>
      <div class="verification-row">
        <input
          name="verification_code"
          type="tel"
          inputmode="numeric"
          maxlength="6"
          value="${escapeHtml(getRegisterVerificationCode())}"
          placeholder="请输入短信验证码"
          required
        >
        <button
          class="mini-button ${secondsLeft ? "" : "mini-button--accent"}"
          data-send-register-code="1"
          type="button"
          ${secondsLeft ? "disabled" : ""}
        >${secondsLeft ? escapeHtml(getSmsSendCooldown(secondsLeft)) : "发送验证码"}</button>
      </div>
      <small class="helper-note">${escapeHtml(helperText)}</small>
    </label>
  `;
}

function createProfilePosts(role, name, summary) {
  return [];
}

function buildProfileFromForm(role, formData, existingProfile) {
  const roleLabel = getRoleLabel(role);
  const city = (formData.get("city") || state.userPosition.city || CITY_PRESETS.xiamen.city).toString();
  const locationLabel = (formData.get("location") || state.userPosition.label || CITY_PRESETS.xiamen.label).toString();
  const intro = (formData.get("intro") || "").toString().trim();
  const avatarFile = formData.get("avatar_file");

  if (role === "gym") {
    const name = (formData.get("gym_name") || existingProfile?.name || `${city} 新场馆`).toString();
    const facilities = (formData.get("facilities") || "").toString();
    const tags = facilities
      .split(/[、,，/\s]+/)
      .map((item) => item.trim())
      .filter(Boolean)
      .slice(0, 4);
    const avatarImage = getUploadedImageUrl(
      avatarFile,
      existingProfile?.avatarImage || createDefaultAvatar(role, name)
    );
    return {
      ...(existingProfile || {}),
      id: existingProfile?.id || `gym-${slugForRole(role)}`,
      role,
      name,
      handle: existingProfile?.handle || `@gym.${String(Date.now()).slice(-4)}`,
      avatar: existingProfile?.avatar || getInitialCharacter(name),
      avatarImage,
      city,
      locationLabel,
      lat: state.userPosition.lat,
      lng: state.userPosition.lng,
      bio: intro || `${name} 已完成入驻，欢迎预约到店训练。`,
      shortDesc: intro || facilities || "设备齐全，欢迎到店体验。",
      price: (formData.get("price") || existingProfile?.price || "¥99/月起").toString(),
      tags: tags.length ? tags : ["器械", "团课", "恢复区"],
      pricingPlans: existingProfile?.pricingPlans || [
        { title: "会员卡", detail: "到店训练 / 团课预约", price: (formData.get("price") || "¥99/月起").toString() }
      ],
      followers: existingProfile?.followers || 0,
      following: existingProfile?.following || 0,
      ratingAvg: existingProfile?.ratingAvg || 0,
      ratingCount: existingProfile?.ratingCount || 0,
      listed: true,
      hours: (formData.get("hours") || "").toString(),
      contactName: (formData.get("contact_name") || "").toString(),
      phone: (formData.get("phone") || "").toString(),
      posts: existingProfile?.posts?.length ? existingProfile.posts : createProfilePosts(role, name, intro || facilities),
      checkins: existingProfile?.checkins || [],
      reviews: existingProfile?.reviews || []
    };
  }

  if (role === "coach") {
    const name = (formData.get("name") || existingProfile?.name || "新教练").toString();
    const specialties = (formData.get("specialties") || "").toString();
    const tags = specialties
      .split(/[、,，/\s]+/)
      .map((item) => item.trim())
      .filter(Boolean)
      .slice(0, 4);
    const avatarImage = getUploadedImageUrl(
      avatarFile,
      existingProfile?.avatarImage || createDefaultAvatar(role, name)
    );
    return {
      ...(existingProfile || {}),
      id: existingProfile?.id || `coach-${slugForRole(role)}`,
      role,
      name,
      handle: existingProfile?.handle || `@coach.${String(Date.now()).slice(-4)}`,
      avatar: existingProfile?.avatar || getInitialCharacter(name),
      avatarImage,
      city,
      locationLabel,
      lat: state.userPosition.lat,
      lng: state.userPosition.lng,
      bio: intro || `${name} 已入驻平台，支持一对一训练和课程预约。`,
      shortDesc: intro || specialties || "擅长减脂塑形、力量提升。",
      price: (formData.get("price") || existingProfile?.price || "¥220/小时").toString(),
      tags: tags.length ? tags : ["减脂", "力量", "私教"],
      pricingPlans: existingProfile?.pricingPlans || [
        { title: "私教课程", detail: "一对一训练服务", price: (formData.get("price") || "¥220/小时").toString() }
      ],
      years: (formData.get("years") || "").toString(),
      certifications: (formData.get("certifications") || "").toString().split(/[、,，/\s]+/).filter(Boolean),
      followers: existingProfile?.followers || 0,
      following: existingProfile?.following || 0,
      ratingAvg: existingProfile?.ratingAvg || 0,
      ratingCount: existingProfile?.ratingCount || 0,
      listed: true,
      posts: existingProfile?.posts?.length ? existingProfile.posts : createProfilePosts(role, name, intro || specialties),
      checkins: existingProfile?.checkins || [],
      reviews: existingProfile?.reviews || []
    };
  }

  const name = (formData.get("name") || existingProfile?.name || "新用户").toString();
  const level = (formData.get("level") || existingProfile?.level || "新手入门").toString();
  const goal = (formData.get("goal") || existingProfile?.goal || "").toString();
  const avatarImage = getUploadedImageUrl(
    avatarFile,
    existingProfile?.avatarImage || createDefaultAvatar(role, name)
  );

  return {
    ...(existingProfile || {}),
    id: existingProfile?.id || `enthusiast-${slugForRole(role)}`,
    role,
    name,
    handle: existingProfile?.handle || `@user.${String(Date.now()).slice(-4)}`,
    avatar: existingProfile?.avatar || getInitialCharacter(name),
    avatarImage,
    city,
    locationLabel,
    lat: state.userPosition.lat,
    lng: state.userPosition.lng,
    bio: intro || `${name} 正在进行 ${level} 训练，目标是 ${goal || "保持规律训练"}。`,
    shortDesc: intro || goal || "开始记录自己的健身生活。",
    price: "",
    tags: [level, city, "训练日记"],
    level,
    goal,
    followers: existingProfile?.followers || 0,
    following: existingProfile?.following || 0,
    ratingAvg: 0,
    ratingCount: 0,
    listed: true,
    posts: existingProfile?.posts?.length ? existingProfile.posts : createProfilePosts(role, name, goal),
    checkins: existingProfile?.checkins || [],
    reviews: existingProfile?.reviews || []
  };
}

async function upsertManagedProfile(role, formData) {
  const profilePayload = await buildRegistrationPayload(role, formData);
  await postAndSync(`${API_BASE}/register`, {
    role,
    profile: profilePayload,
    verificationCode: isSmsVerificationEnabled() ? (formData.get("verification_code") || "").toString().trim() : "",
    account: state.managedAccounts[0]
      ? {
          accountId: state.managedAccounts[0].id,
          restoreToken: state.managedAccounts[0].restoreToken
        }
      : undefined
  });
  rememberManagedAccounts(state.managedAccounts);
  state.activeProfileId = state.currentActorProfileId;
  state.composeProfileId = state.currentActorProfileId;
  state.selectedRole = role;
  state.activePage = "home";
  state.locationStatus = `${getRoleLabel(role)}注册成功，现在这个设备会记住你的身份，并和其他测试用户共享互动数据。`;
  syncNavActive();
  closeOverlay();
  renderPage();
}

async function submitAuthLogin() {
  let role = state.authRole;
  const phone = normalizePhone(state.authPhone);
  const canUseToken = Boolean(state.authAccountId && state.authRestoreToken);
  if (!canUseToken && !phone) {
    throw new Error("请输入注册时填写的手机号。");
  }

  if (phone && !canUseToken) {
    const matches = await lookupAuthMatches(phone, { silent: true });
    const selectedMatch = matches.find((item) => item.role === role);

    if (!matches.length) {
      const recovered = await recoverAccountFromSnapshot(role, phone);
      if (recovered) {
        state.selectedRole = role;
        state.activePage = "home";
        state.activeProfileId = state.currentActorProfileId;
        state.composeProfileId = state.currentActorProfileId;
        state.locationStatus = `${getRoleLabel(role)}已从本机缓存恢复并登录成功。`;
        state.authMatches = [];
        closeOverlay();
        syncNavActive();
        renderPage();
        return;
      }
      throw new Error("没有找到这个手机号下的已注册身份，请先注册后再登录。");
    }

    if (!selectedMatch && matches.length === 1) {
      role = matches[0].role;
      state.authRole = role;
      state.authMessage = `已自动识别为 ${getRoleLabel(role)}，现在可以直接登录。`;
    } else if (!selectedMatch && matches.length > 1) {
      state.authMessage = "这个手机号下有多个已注册身份，请先点上方身份卡选择要登录的角色。";
      renderOverlay();
      throw new Error("请选择要登录的身份。");
    }
  }

  if (!roleConfig[role]) {
    throw new Error("请先选择要登录的身份。");
  }

  try {
    try {
      await postAndSync(`${API_BASE}/auth/login`, {
        role,
        phone,
        verificationCode: state.authVerificationCode,
        accountId: state.authAccountId,
        restoreToken: state.authRestoreToken
      }, { keepOverlay: true });
      state.authMessage = "";
    } catch (error) {
      if (!(canUseToken && phone)) {
        throw error;
      }

      state.authAccountId = "";
      state.authRestoreToken = "";

      await postAndSync(`${API_BASE}/auth/login`, {
        role,
        phone,
        verificationCode: state.authVerificationCode,
        accountId: "",
        restoreToken: ""
      }, { keepOverlay: true });
      state.authMessage = "检测到本机旧凭证已失效，已自动改用手机号找回并刷新这个账号。";
    }
  } catch (error) {
    if (!(phone && (await recoverAccountFromSnapshot(role, phone)))) {
      throw error;
    }
  }

  if (!state.followSet.size) {
    await maybeRestoreFollowState({ force: true });
  }

  rememberManagedAccounts(state.managedAccounts);
  state.selectedRole = role;
  state.activePage = "home";
  state.activeProfileId = state.currentActorProfileId;
  state.composeProfileId = state.currentActorProfileId;
  state.locationStatus = `${getRoleLabel(role)}登录成功，这个设备会继续记住你的账号。`;
  state.authMatches = [];
  closeOverlay();
  syncNavActive();
  renderPage();
}

async function submitRating(profileId) {
  const profile = getProfile(profileId);
  const rate = Number(state.ratingDrafts[profileId] || 0);
  const text = (state.reviewDrafts[profileId] || "").trim();

  if (!profile || !rate) return;
  await postAndSync(`${API_BASE}/rate`, {
    targetProfileId: profileId,
    score: rate,
    text
  });
  state.ratingDrafts[profileId] = 0;
  state.reviewDrafts[profileId] = "";
  renderPage();
}

async function submitComposePost() {
  const profile = getProfile(state.composeProfileId);
  if (!profile) return;
  const content = state.composeContent.trim();
  if (!content && !state.composeMedia.length) return;
  await postAndSync(`${API_BASE}/post/create`, {
    profileId: profile.id,
    content: content || "分享了一条新的媒体动态。",
    meta: `${getRoleLabel(profile.role)} · ${state.userPosition.label}`,
    media: state.composeMedia
      .map((item) => serializeManagedMediaItem(item))
      .filter(Boolean)
  });
  state.currentActorProfileId = profile.id;
  state.activeProfileId = profile.id;
  state.activePage = "profile";
  state.profileSubpage = "";
  state.composeContent = "";
  state.composeMeta = "";
  state.composeMedia = [];
  syncNavActive();
  closeOverlay();
  renderPage();
}

function toggleCommonSportSelection(sportId) {
  const profile = getMyPageProfile();
  if (!profile || profile.role !== "enthusiast") {
    return;
  }

  const current = state.checkinSelectionDraft.length ? [...state.checkinSelectionDraft] : [...(profile.favoriteSports || [])];
  if (current.includes(sportId)) {
    state.checkinSelectionDraft = current.filter((item) => item !== sportId);
  } else {
    state.checkinSelectionDraft = [...current, sportId].slice(0, 6);
  }
  renderPage();
}

async function selectWorkoutSport(sportId) {
  if (!sportId) return;
  if (state.workoutSession) {
    return;
  }
  state.checkinCurrentSportId = sportId;
  renderPage();
}

function openCheckinEditor() {
  const profile = getMyPageProfile();
  if (!profile) return;
  state.checkinEditing = true;
  state.checkinSelectionDraft = [...(profile.favoriteSports || [])];
  renderPage();
}

function cancelCheckinEditor() {
  state.checkinEditing = false;
  state.checkinSelectionDraft = [];
  renderPage();
}

async function saveFavoriteSports() {
  const profile = getMyPageProfile();
  const favoriteSports = [...state.checkinSelectionDraft];
  if (!profile || profile.role !== "enthusiast") {
    throw new Error("请先用健身爱好者身份注册后再设置运动项目。");
  }
  if (!favoriteSports.length) {
    throw new Error("请至少选择一个常规运动项目。");
  }

  await postAndSync(`${API_BASE}/profile/preferences`, {
    profileId: profile.id,
    favoriteSports
  });

  state.checkinEditing = false;
  state.checkinSelectionDraft = [];
  state.checkinCurrentSportId = favoriteSports[0] || "";
  renderPage();
}

async function startWorkoutSession(sportId = "") {
  if (state.workoutFinishing?.status === "saving") {
    throw new Error("上一条打卡还在保存，请稍等 1-2 秒。");
  }
  const profile = getMyPageProfile();
  if (!profile || profile.role !== "enthusiast") {
    throw new Error("请先用健身爱好者身份注册后再开始运动。");
  }
  if (!profile.gender || !getProfileHeight(profile) || !getProfileWeight(profile)) {
    state.profileSubpage = "health";
    renderPage();
    throw new Error("请先完善性别、身高和体重，再开始运动。");
  }

  const targetSport = sportId || state.checkinCurrentSportId || getCurrentWorkoutSport(profile)?.id || "";
  if (!targetSport) {
    state.profileSubpage = "checkin";
    state.checkinEditing = true;
    renderPage();
    throw new Error("第一次打卡请先选择日常训练项目，再开始运动。");
  }

  state.checkinCurrentSportId = targetSport;
  state.outdoorShareCheckinId = "";
  const gps = supportsOutdoorRouteShare(targetSport) ? await startOutdoorGpsTracking(targetSport) : null;
  state.workoutSession = {
    sportId: targetSport,
    startedAt: Date.now(),
    pausedAt: 0,
    pausedDurationMs: 0,
    gps
  };
  state.activePage = "profile";
  state.profileSubpage = "checkin";
  appView.scrollTop = 0;
  renderPage();
}

function cancelWorkoutSession() {
  stopOutdoorGpsTracking();
  state.workoutSession = null;
  renderPage();
}

async function toggleWorkoutPause() {
  const session = state.workoutSession;
  if (!session) return;

  if (session.pausedAt) {
    session.pausedDurationMs = Number(session.pausedDurationMs || 0) + Math.max(0, Date.now() - session.pausedAt);
    session.pausedAt = 0;
    if (supportsOutdoorRouteShare(session.sportId)) {
      session.gps = await resumeOutdoorGpsTracking(session.sportId, session.gps);
    }
  } else {
    session.pausedAt = Date.now();
    if (supportsOutdoorRouteShare(session.sportId)) {
      pauseOutdoorGpsTracking(session.gps);
      if (session.gps) {
        session.gps.status = "已暂停定位记录";
      }
    }
  }

  renderPage();
}

async function finishWorkoutSession() {
  const profile = getMyPageProfile();
  const liveSession = state.workoutSession;
  const session = getWorkoutSessionStats(profile);
  if (!profile || !session || !liveSession) return;
  if (state.workoutFinishing?.status === "saving") return;

  state.pendingFinishedWorkout = {
    profileId: profile.id,
    profileSnapshot: deepClone(profile),
    sessionState: deepClone(liveSession)
  };
  stopOutdoorGpsTracking(liveSession.gps);
  state.workoutSession = null;
  state.workoutFinishing = {
    status: "saving",
    sportId: session.sport.id,
    sportLabel: session.sport.label,
    startedAt: Date.now(),
    message: "正在保存这次训练..."
  };
  state.activePage = "profile";
  state.profileSubpage = "checkin";
  if (appView) appView.scrollTop = 0;
  renderPage();

  try {
    await persistFinishedWorkout();
  } catch (error) {
    state.workoutFinishing = {
      status: "failed",
      sportId: session.sport.id,
      sportLabel: session.sport.label,
      startedAt: Date.now(),
      message: error?.message || "这次训练暂时没有保存成功。"
    };
    renderPage();
    throw error;
  }
}

async function retryFinishedWorkoutSave() {
  const draft = state.pendingFinishedWorkout;
  if (!draft || state.workoutFinishing?.status === "saving") return;
  const sport = getCheckinSport(draft.sessionState?.sportId);
  state.workoutFinishing = {
    status: "saving",
    sportId: draft.sessionState?.sportId || "",
    sportLabel: sport?.label || "本次训练",
    startedAt: Date.now(),
    message: "正在重新保存这次训练..."
  };
  renderPage();

  try {
    await persistFinishedWorkout({ forceFinalPoint: true });
  } catch (error) {
    state.workoutFinishing = {
      status: "failed",
      sportId: draft.sessionState?.sportId || "",
      sportLabel: sport?.label || "本次训练",
      startedAt: Date.now(),
      message: error?.message || "重试失败，请稍后再试。"
    };
    renderPage();
    throw error;
  }
}

async function importHealthDevice(source) {
  const profile = getMyPageProfile();
  if (!profile || profile.role !== "enthusiast") {
    throw new Error("请先注册后再同步健康设备。");
  }

  await postAndSync(`${API_BASE}/health/device-sync`, {
    profileId: profile.id,
    source
  });
  renderPage();
}

async function togglePostLike(postId) {
  const found = getPostById(postId);
  if (!found?.post) return;

  const previousLiked = Boolean(found.post.likedByCurrentActor);
  const previousLikeCount = Number(found.post.likeCount || 0);
  const nextLiked = !previousLiked;
  const nextLikeCount = Math.max(0, previousLikeCount + (previousLiked ? -1 : 1));
  const mutation =
    state.likeMutationQueue.get(postId) ||
    {
      queued: 0,
      inFlight: false,
      confirmedLiked: previousLiked,
      confirmedLikeCount: previousLikeCount,
      desiredLiked: previousLiked,
      desiredLikeCount: previousLikeCount
    };

  mutation.queued += 1;
  mutation.desiredLiked = nextLiked;
  mutation.desiredLikeCount = nextLikeCount;
  state.likeMutationQueue.set(postId, mutation);

  applyPostLikeState(postId, nextLiked, nextLikeCount);
  refreshPostLikeButtons(postId);
  flushPostLikeQueue(postId);
}

async function togglePostFavorite(postId) {
  const found = getPostById(postId);
  if (!found?.post || !isMediaPost(found.post)) return;

  const previousFavorited = state.favoritePostIds.has(postId);
  const nextFavorited = !previousFavorited;
  const mutation =
    state.favoriteMutationQueue.get(postId) ||
    {
      queued: 0,
      inFlight: false,
      confirmedFavorited: previousFavorited,
      desiredFavorited: previousFavorited
    };

  mutation.queued += 1;
  mutation.desiredFavorited = nextFavorited;
  state.favoriteMutationQueue.set(postId, mutation);

  applyPostFavoriteState(postId, nextFavorited);
  refreshPostFavoriteButtons(postId);
  flushPostFavoriteQueue(postId);
}

async function submitPostComment(postId) {
  const text = (state.commentDrafts[postId] || "").trim();
  if (!text) return;

  const previousDraft = state.commentDrafts[postId] || "";
  const optimisticCommentId = insertOptimisticComment(postId, text);
  state.commentDrafts[postId] = "";
  refreshPostCommentViews(postId);

  try {
    const payload = await postWithoutStateSync(`${API_BASE}/post/comment`, { postId, text });
    applyConfirmedPostState(postId, getPayloadPostById(payload, postId));
  } catch (error) {
    removeOptimisticComment(postId, optimisticCommentId);
    if (!state.commentDrafts[postId]) {
      state.commentDrafts[postId] = previousDraft;
    }
    refreshPostCommentViews(postId);
    throw error;
  }

  refreshPostCommentViews(postId);
}

async function sendDirectMessage(profileId) {
  const text = state.chatDraft.trim();
  if (!text) return;

  const previousDraft = state.chatDraft;
  state.chatDraft = "";
  const optimisticMessageId = insertOptimisticMessage(profileId, text);
  state.overlayMode = "chat";
  renderOverlay();

  try {
    const payload = await postWithoutStateSync(`${API_BASE}/message/send`, {
      targetProfileId: profileId,
      text
    });
    const confirmedThread =
      payload?.thread ||
      (payload?.threads || []).find((thread) => thread.withProfileId === profileId);
    mergeConfirmedThread(profileId, confirmedThread, optimisticMessageId);
  } catch (error) {
    removeOptimisticMessage(profileId, optimisticMessageId);
    if (!state.chatDraft) {
      state.chatDraft = previousDraft;
    }
    throw error;
  } finally {
    state.overlayMode = "chat";
    renderOverlay();
  }
}

async function createBooking(profileId, plan = null) {
  await postAndSync(`${API_BASE}/booking/create`, {
    targetProfileId: profileId,
    plan
  });
  state.activePage = "booking";
  syncNavActive();
  renderPage();
  appView.scrollTop = 0;
}

async function selectRole(role) {
  const managedProfile = getManagedProfileByRole(role);
  await postAndSync(`${API_BASE}/session/select`, {
    selectedRole: role,
    currentActorProfileId: managedProfile?.id || ""
  }, { keepOverlay: true });
  state.selectedRole = role;
  if (managedProfile?.id) {
    state.currentActorProfileId = managedProfile.id;
    state.composeProfileId = managedProfile.id;
    if (state.activePage === "profile") {
      state.activeProfileId = managedProfile.id;
      state.profileSubpage = "";
    }
  }
  renderPage();
}

function renderHomeCards() {
  const role = state.activeHomeTab;
  const profiles = getHomeProfiles(role);

  return `
    <section class="card-grid">
      ${
        profiles.length
          ? profiles
              .map(
                (profile) => {
                  const followed = state.followSet.has(profile.id);

                  return `
                  <article class="card card--interactive" data-open-profile="${profile.id}">
                    ${renderCardCover(profile)}
                    <div class="card-copy">
                      <div class="card-title-row">
                        ${renderAvatarMarkup(profile, "avatar avatar--card")}
                        <div class="card-title-copy">
                          <h3>${escapeHtml(profile.name)}</h3>
                          <p class="card-role">${escapeHtml(getRoleLabel(profile.role))}</p>
                        </div>
                      </div>
                      <div class="meta-line">
                        <span><strong class="star">★ ${getRatingDisplay(profile)}</strong></span>
                        <span>${formatDistance(profile.distanceMeters)}</span>
                      </div>
                      <p class="desc">${escapeHtml(profile.shortDesc)}</p>
                      <div class="price-line">
                        <span class="price">${escapeHtml(profile.price || "查看主页")}</span>
                        <button class="follow-button follow-button--card ${followed ? "is-active" : ""}" type="button" data-toggle-follow="${profile.id}">
                          ${followed ? "已关注" : "关注"}
                        </button>
                      </div>
                    </div>
                  </article>
                `;
                }
              )
              .join("")
          : '<article class="empty-card">没有匹配结果，换个关键词试试。</article>'
      }
    </section>
  `;
}

function renderHome() {
  const homeProfiles = getHomeProfiles(state.activeHomeTab);
  const titleMap = {
    gym: ["附近健身房", "精选场馆"],
    coach: ["附近教练", "精选教练"]
  };

  appView.innerHTML = `
    <section class="home-screen">
      <div class="home-static">
        <div class="top-utility top-utility--home">
          <button class="location-switch" data-open-city="1" type="button">
            <span class="pin"></span>
            <strong>${escapeHtml(state.userPosition.label)}</strong>
          </button>
          <div class="top-action-group">
            <button class="utility-chip" data-action="locate" type="button" aria-label="实时定位">
              <span class="locate-icon"></span>
              <span>定位</span>
            </button>
            <button class="utility-chip utility-chip--accent" data-open-role-picker="1" type="button">
              我是${escapeHtml(roleConfig[state.selectedRole].short)}
            </button>
          </div>
        </div>

        <section class="search-box">
          <input data-search-input="1" type="text" value="${escapeHtml(state.searchKeyword)}" placeholder="搜索健身房、教练、课程" aria-label="搜索">
          <button type="button" aria-label="搜索">
            <span class="search-icon"></span>
          </button>
        </section>

        <nav class="tabs">
          <button class="tab ${state.activeHomeTab === "gym" ? "is-active" : ""}" data-home-tab="gym" type="button">健身房</button>
          <button class="tab ${state.activeHomeTab === "coach" ? "is-active" : ""}" data-home-tab="coach" type="button">教练</button>
        </nav>

        <section class="section-head">
          <h2>${titleMap[state.activeHomeTab][0]}</h2>
          <h2>${titleMap[state.activeHomeTab][1]}</h2>
        </section>
        <p class="result-tip">按距离排序 · 共 ${homeProfiles.length} 条结果</p>
      </div>

      <div class="home-scroll-area">
        ${renderHomeCards()}
      </div>
    </section>
  `;
}

function renderDiscover() {
  const recommendedProfiles = getRecommendedProfiles();
  const discoverFeed = getFollowingFeedItems();

  appView.innerHTML = `
    <section class="page-header">
      <div>
        <p class="page-label">Discover</p>
        <h1>探索</h1>
      </div>
      <button class="mini-button mini-button--accent" data-open-followers="1" type="button">我的粉丝</button>
    </section>

    <section class="section-title-row section-title-row--discover-recommended">
      <div>
        <h3>推荐关注</h3>
        <p class="result-tip">按可能认识、粉丝较多、评分较高三类推荐，优先展示附近的人</p>
      </div>
    </section>

    <section class="discover-avatar-rail">
      ${recommendedProfiles
        .map((profile) => {
          return `
            <article class="discover-avatar-card">
              <button class="discover-avatar-button" data-open-profile="${profile.id}" type="button">
                ${renderAvatarMarkup(profile, "avatar avatar--discover")}
                <strong>${escapeHtml(profile.name)}</strong>
                <p>${escapeHtml(getRoleLabel(profile.role))}</p>
                <small class="discover-avatar-reason">${escapeHtml(profile.recommendReason || "推荐关注")} · ${escapeHtml(profile.recommendDetail || "")}</small>
              </button>
              <button class="follow-button" data-toggle-follow="${profile.id}" type="button">关注</button>
            </article>
          `;
        })
        .join("")}
      ${
        !recommendedProfiles.length
          ? `
            <article class="empty-card empty-card--compact">
              你已经关注完当前推荐对象了，可以直接看下面的关注动态。
            </article>
          `
          : ""
      }
    </section>

    <section class="section-title-row section-title-row--discover-feed">
      <div>
        <h3>关注动态</h3>
        <p class="result-tip">按更新时间排序，只显示你已关注的对象</p>
      </div>
      <button class="mini-button" data-open-city="1" type="button">切换城市</button>
    </section>

    <section class="discover-feed-list">
      ${
        discoverFeed.length
          ? discoverFeed
              .map((item) => item.kind === "profile"
                ? renderDiscoverProfileEntry(item.profile)
                : renderPostCard(item.profile, item.post, { compact: true }))
              .join("")
          : `
            <article class="empty-card">
              你还没有关注任何对象。先在上面的推荐关注里选几个，下面就会按更新时间展示他们的最新动态。
            </article>
          `
      }
    </section>
  `;
}

function renderBooking() {
  const myProfile = getMyPageProfile();
  const bookingList = myProfile ? getRelevantBookingsForProfile(myProfile) : [];
  const bookingDashboard = myProfile ? getBookingDashboard(myProfile) : { pendingCount: 0, weeklyCheckins: 0, points: 0 };
  const emptyText = myProfile?.role === "enthusiast"
    ? "你还没有正式预约。去首页、探索或教练/场馆主页选择价格方案后，这里才会出现排期和订单。"
    : myProfile?.role === "coach"
      ? "现在还没有学员给你发来预约。完善课程价格、动态和主页介绍后，这里会出现新的订单。"
      : "现在还没有用户预约你的场馆。完善设施、价格和主页后，这里会出现新的订单。";
  appView.innerHTML = `
    <section class="page-header">
      <div>
        <p class="page-label">Booking</p>
        <h1>预约</h1>
      </div>
      <button class="mini-button" data-open-role-picker="1" type="button">切换身份</button>
    </section>

    <article class="summary-card">
      <div>
        <span>${escapeHtml(bookingDashboard.pendingLabel || "本周待上课")}</span>
        <strong>${bookingDashboard.pendingCount}</strong>
      </div>
      <div>
        <span>本周打卡</span>
        <strong>${bookingDashboard.weeklyCheckins}</strong>
      </div>
      <div>
        <span>积分</span>
        <strong>${bookingDashboard.points}</strong>
      </div>
    </article>

    <section class="stack-list">
      ${renderManagedBookingList(myProfile, bookingList, {
        emptyText,
        primaryAction: myProfile?.role === "enthusiast" ? "查看主页" : "查看预约"
      })}
    </section>

    <article class="helper-card">
      <strong>预约说明</strong>
      <p>${myProfile?.role === "enthusiast" ? "教练与健身房的定价会同步展示在首页卡片、主页定价模块和探索流里；完成正式预约后，本页才会出现待上课与订单内容。" : "现在这页会优先展示别人给你的订单和预约消息，方便教练与健身房直接管理到店与排期。"}</p>
    </article>
  `;
}

function renderRatingStars(profileId, activeValue) {
  return `
    <div class="rating-stars">
      ${[1, 2, 3, 4, 5]
        .map(
          (value) => `
            <button class="rating-star ${value <= activeValue ? "is-active" : ""}" type="button" data-rate-profile="${profileId}" data-rate-value="${value}">
              ★
            </button>
          `
        )
        .join("")}
    </div>
  `;
}

function renderPostMedia(post) {
  if (!post.media || !post.media.length) return "";

  return `
    <div class="timeline-media-grid ${post.media.length === 1 ? "is-single" : ""}">
      ${post.media
        .map((item, index) => {
          const openButton = `
            <button
              class="timeline-media-open"
              data-open-media-detail="${post.id}"
              data-media-index="${index}"
              type="button"
              aria-label="查看媒体详情"
            >
              查看
            </button>
          `;
          if (item.type === "video") {
            return `
              <div class="timeline-media-card image-shell image-shell--cover is-loaded">
                ${openButton}
                <video class="timeline-media-video" src="${getMediaDisplayUrl(item)}" poster="${escapeHtml(getMediaThumbnailUrl(item, "feed"))}" controls playsinline preload="metadata"></video>
              </div>
            `;
          }

          return `
            <div class="timeline-media-card image-shell image-shell--cover">
              ${openButton}
              <img class="timeline-media-image" src="${escapeHtml(getMediaThumbnailUrl(item, "feed"))}" alt="${escapeHtml(item.name || "动态图片")}" loading="lazy" decoding="async">
            </div>
          `;
        })
        .join("")}
    </div>
  `;
}

function canOpenChatWith(profileId) {
  return Boolean(
    profileId &&
      !isManagedProfile(profileId) &&
      state.currentActorProfileId &&
      state.followSet.has(profileId)
  );
}

function renderPostComments(post) {
  return `
    <section class="post-comment-list">
      ${(post.comments || [])
        .map(
          (comment) => `
            <article class="post-comment-item">
              ${renderAvatarMarkup({ name: comment.authorName, avatarImage: comment.authorAvatarImage, avatar: comment.authorName?.[0] || "?" }, "avatar avatar--comment")}
              <div class="post-comment-body">
                <div class="post-comment-head">
                  <strong>${escapeHtml(comment.authorName)}</strong>
                  <span>${escapeHtml(comment.time)}</span>
                </div>
                <p>${escapeHtml(comment.text)}</p>
              </div>
            </article>
          `
        )
        .join("")}
    </section>
  `;
}

function renderPostActionGlyph(kind, active = false) {
  const common = 'class="post-action-glyph" viewBox="0 0 24 24" aria-hidden="true" focusable="false"';
  if (kind === "like") {
    const heartPath = "M12 20.6l-.72-.66C5.72 14.87 2.4 11.83 2.4 8.09 2.4 5.19 4.63 3 7.45 3c1.61 0 3.15.75 4.15 1.94C12.6 3.75 14.14 3 15.75 3 18.57 3 20.8 5.19 20.8 8.09c0 3.74-3.32 6.78-8.88 11.85l-.72.66z";
    return `<svg ${common}><path d="${heartPath}" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"/></svg>`;
  }

  if (kind === "favorite") {
    return `<svg ${common}><path d="M12 3.8l2.54 5.14 5.67.82-4.11 4 0.97 5.64L12 16.78l-5.07 2.62 0.97-5.64-4.11-4 5.67-.82L12 3.8z" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round"/></svg>`;
  }

  return `<svg ${common}><path d="M6 7.2h12a3 3 0 0 1 3 3v5.1a3 3 0 0 1-3 3H9.8l-4.6 3v-3H6a3 3 0 0 1-3-3v-5.1a3 3 0 0 1 3-3z" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg>`;
}

function renderPostCard(profile, post, options = {}) {
  const { compact = false, showProfileButton = true } = options;
  const commentDraft = state.commentDrafts[post.id] || "";
  const showChatButton = canOpenChatWith(profile.id);
  const canFavorite = isMediaPost(post);
  const favorited = state.favoritePostIds.has(post.id);
  const checkinMeta = post.checkin
    ? `
        <div class="checkin-inline-row">
          <span>${escapeHtml(post.checkin.sportLabel || "训练打卡")}</span>
          <span>${escapeHtml(`${post.checkin.duration || 0} 分钟`)}</span>
          ${post.checkin.calories ? `<span>${escapeHtml(`${post.checkin.calories} kcal`)}</span>` : ""}
          ${post.checkin.distance ? `<span>${escapeHtml(`${post.checkin.distance} km`)}</span>` : ""}
        </div>
      `
    : "";

  return `
    <article class="timeline-card ${compact ? "timeline-card--compact" : ""}" data-post-card="${escapeHtml(post.id)}">
      <div class="timeline-head">
        ${
          showProfileButton
            ? `
              <button class="timeline-author timeline-author-button" data-open-profile="${profile.id}" type="button">
                ${renderAvatarMarkup(profile, "avatar")}
                <div>
                  <strong>${escapeHtml(profile.name)}</strong>
                  <p>${escapeHtml(profile.handle)} · ${escapeHtml(post.time)}</p>
                </div>
              </button>
            `
            : `
              <div class="timeline-author">
                ${renderAvatarMarkup(profile, "avatar")}
                <div>
                  <strong>${escapeHtml(profile.name)}</strong>
                  <p>${escapeHtml(profile.handle)} · ${escapeHtml(post.time)}</p>
                </div>
              </div>
            `
        }
        <span>${escapeHtml(getRoleLabel(profile.role))}</span>
      </div>
      <p>${escapeHtml(post.content)}</p>
      ${checkinMeta}
      ${renderPostMedia(post)}
      <small>${escapeHtml(post.meta)}</small>
      <div class="post-action-bar">
        <button class="post-action-button post-action-button--icon ${post.likedByCurrentActor ? "is-active" : ""}" data-like-post="${post.id}" type="button" aria-label="${post.likedByCurrentActor ? "取消点赞" : "点赞"}">
          ${renderPostActionGlyph("like", post.likedByCurrentActor)}
          <span class="post-action-number">${post.likeCount || 0}</span>
        </button>
        ${
          canFavorite
            ? `<button class="post-action-button post-action-button--icon post-action-button--favorite ${favorited ? "is-active" : ""}" data-favorite-post="${post.id}" type="button" aria-label="${favorited ? "取消收藏" : "收藏"}">${renderPostActionGlyph("favorite", favorited)}<span class="post-action-number">${getPostFavoriteDisplayCount(post)}</span></button>`
            : ""
        }
        <span class="post-action-button post-action-button--icon post-action-button--count">${renderPostActionGlyph("comment", false)}<span class="post-action-number">${post.comments?.length || 0}</span></span>
        ${
          showChatButton
            ? `<button class="post-action-button" data-open-chat="${profile.id}" type="button">私信</button>`
            : ""
        }
      </div>
      ${renderPostComments(post)}
      <div class="post-comment-composer">
        <input data-comment-input="${post.id}" type="text" value="${escapeHtml(commentDraft)}" placeholder="写评论，和对方互动一下">
        <button class="mini-button mini-button--accent" data-comment-post="${post.id}" type="button">发送</button>
      </div>
    </article>
  `;
}

function renderProfileTimeline(profile) {
  return `
    <section class="timeline-list">
      ${(profile.posts || []).map((post) => renderPostCard(profile, post, { showProfileButton: false })).join("")}
    </section>
  `;
}

function getProfilePricingPlans(profile) {
  if (profile.pricingPlans?.length) return profile.pricingPlans;

  if (profile.role === "gym") {
    return [
      { title: "会员卡", detail: "到店训练 / 团课预约", price: profile.price || "¥99/月起" }
    ];
  }

  if (profile.role === "coach") {
    return [
      { title: "私教课程", detail: "一对一训练服务", price: profile.price || "¥220/小时" }
    ];
  }

  return [];
}

function renderProfileFeatureSection(profile) {
  if (profile.role === "enthusiast") {
    return `
      <article class="detail-card">
        <div class="section-title-row">
          <h3>训练档案</h3>
          <span class="score-pill">测试模块</span>
        </div>
        <div class="detail-grid">
          <div class="detail-item">
            <span>训练等级</span>
            <strong>${escapeHtml(profile.level || "未填写")}</strong>
          </div>
          <div class="detail-item">
            <span>训练目标</span>
            <strong>${escapeHtml(profile.goal || "保持规律训练")}</strong>
          </div>
          <div class="detail-item">
            <span>常驻定位</span>
            <strong>${escapeHtml(profile.locationLabel)}</strong>
          </div>
        </div>
      </article>
    `;
  }

  const pricingPlans = getProfilePricingPlans(profile);
  return `
    <article class="detail-card">
      <div class="section-title-row">
        <h3>${profile.role === "gym" ? "场馆定价" : "课程定价"}</h3>
        <button class="mini-button mini-button--accent" data-create-booking="${profile.id}" type="button">立即预约</button>
      </div>
      <div class="detail-grid">
        ${pricingPlans
          .map(
            (plan) => `
              <article class="detail-item detail-item--price">
                <span>${escapeHtml(plan.title)}</span>
                <strong>${escapeHtml(plan.price)}</strong>
                <p>${escapeHtml(plan.detail)}</p>
                <button class="mini-button" data-create-booking="${profile.id}" data-plan-index="${pricingPlans.indexOf(plan)}" type="button">预约这个</button>
              </article>
            `
          )
          .join("")}
      </div>
      <p class="helper-note helper-note--detail">
        ${profile.role === "gym"
          ? `营业时间：${escapeHtml(profile.hours || "未填写")} · 定位：${escapeHtml(profile.locationLabel)}`
          : `从业时间：${escapeHtml(profile.years || "未填写")} 年 · 定位：${escapeHtml(profile.locationLabel)}`}
      </p>
    </article>
  `;
}

function findCheckinSport(optionId) {
  return CHECKIN_SPORTS.find((item) => item.id === optionId) || null;
}

function getCheckinSport(optionId) {
  return findCheckinSport(optionId) || CHECKIN_SPORTS[0];
}

function getCheckinMetrics(optionId) {
  return CHECKIN_SPORT_METRICS[optionId] || CHECKIN_SPORT_METRICS.run;
}

function getSafeDate(value) {
  const date = value ? new Date(value) : null;
  return Number.isNaN(date?.getTime()) ? null : date;
}

function isSameLocalDay(left, right) {
  return (
    left &&
    right &&
    left.getFullYear() === right.getFullYear() &&
    left.getMonth() === right.getMonth() &&
    left.getDate() === right.getDate()
  );
}

function getWeekAnchor(date) {
  const anchor = new Date(date);
  const day = anchor.getDay();
  const diff = day === 0 ? 6 : day - 1;
  anchor.setHours(0, 0, 0, 0);
  anchor.setDate(anchor.getDate() - diff);
  return anchor;
}

function formatWorkoutTimer(totalSeconds) {
  const safeSeconds = Math.max(0, Math.floor(totalSeconds || 0));
  const hours = String(Math.floor(safeSeconds / 3600)).padStart(2, "0");
  const minutes = String(Math.floor((safeSeconds % 3600) / 60)).padStart(2, "0");
  const seconds = String(safeSeconds % 60).padStart(2, "0");
  return `${hours}:${minutes}:${seconds}`;
}

function formatWorkoutDurationLabel(totalSeconds) {
  const safeSeconds = Math.max(0, Math.floor(totalSeconds || 0));
  const hours = Math.floor(safeSeconds / 3600);
  const minutes = String(Math.floor((safeSeconds % 3600) / 60)).padStart(2, "0");
  const seconds = String(safeSeconds % 60).padStart(2, "0");
  return `${hours}:${minutes}:${seconds}`;
}

function formatWorkoutPaceLabel(durationMinutes, distanceKm) {
  if (!distanceKm || distanceKm <= 0) return "--";
  const totalSeconds = Math.max(1, Math.round((Number(durationMinutes || 0) * 60) / distanceKm));
  const minutes = Math.floor(totalSeconds / 60);
  const seconds = String(totalSeconds % 60).padStart(2, "0");
  return `${minutes}'${seconds}"`;
}

function formatShareDateLabel(dateInput) {
  const date = getSafeDate(dateInput) || new Date();
  return date.toLocaleString("zh-CN", {
    month: "numeric",
    day: "numeric",
    hour: "numeric",
    minute: "2-digit"
  });
}

function supportsOutdoorRouteShare(sportId) {
  return OUTDOOR_ROUTE_SPORT_IDS.has(sportId);
}

function getOutdoorGpsStatus(session) {
  if (!session?.gps) return "";
  const status = session.gps.status || "";
  const pointCount = Array.isArray(session.gps.points) ? session.gps.points.length : 0;
  return pointCount > 1 ? `${status} · 已记录 ${pointCount} 个定位点` : status;
}

function getGeoPositionErrorMessage(error) {
  if (!error) return "定位失败，请检查浏览器权限。";
  if (error.code === 1) return "户外运动需要定位权限，请允许浏览器访问你的位置。";
  if (error.code === 2) return "暂时无法获取定位，请移动到空旷区域后重试。";
  if (error.code === 3) return "定位超时，请检查网络和定位权限后重试。";
  return error.message || "定位失败，请稍后再试。";
}

function getGeoPointAltitude(coords = {}) {
  const altitude = Number(coords.altitude);
  return Number.isFinite(altitude) ? altitude : null;
}

function buildGeoPoint(position) {
  return {
    lat: Number(position.coords.latitude),
    lng: Number(position.coords.longitude),
    accuracy: Number(position.coords.accuracy || 0),
    altitude: getGeoPointAltitude(position.coords),
    recordedAt: new Date(position.timestamp || Date.now()).toISOString()
  };
}

function getOutdoorSpeedLimit(sportId) {
  const limitBySport = {
    run: 7.5,
    "trail-run": 7,
    "outdoor-walk": 3,
    hiking: 3.2,
    "outdoor-cycling": 18
  };
  return limitBySport[sportId] || 8;
}

function appendWorkoutGeoPoint(position, sportId, gpsState = null) {
  const gps = gpsState || state.workoutSession?.gps;
  if (!gps) return;
  const point = buildGeoPoint(position);
  gps.status = point.accuracy ? `GPS 已连接 · 精度 ${Math.round(point.accuracy)}m` : "GPS 已连接";
  gps.lastAccuracy = point.accuracy || 0;

  if (!gps.points.length) {
    gps.points = [point];
    return;
  }

  const lastPoint = gps.points[gps.points.length - 1];
  const segmentMeters = getDistanceMeters(
    { lat: lastPoint.lat, lng: lastPoint.lng },
    { lat: point.lat, lng: point.lng }
  );
  const elapsedSeconds = Math.max(
    1,
    Math.round(
      (new Date(point.recordedAt).getTime() - new Date(lastPoint.recordedAt).getTime()) / 1000
    )
  );
  const speedMps = segmentMeters / elapsedSeconds;
  const maxSpeed = getOutdoorSpeedLimit(sportId);
  const accuracyLimit = Math.max(4, Math.min(point.accuracy || 12, 16));
  const minSegmentMeters = gps.points.length < 2 ? 0.8 : Math.min(Math.max(1.2, accuracyLimit * 0.35), 3.2);
  const hasMeaningfulTimeGap = elapsedSeconds >= 12 && segmentMeters >= 0.8;
  const accuracyImproved =
    typeof point.accuracy === "number" &&
    typeof lastPoint.accuracy === "number" &&
    point.accuracy + 4 < lastPoint.accuracy;

  if ((segmentMeters < minSegmentMeters && !hasMeaningfulTimeGap && !accuracyImproved) || speedMps > maxSpeed) {
    return;
  }

  gps.points.push(point);
  gps.totalDistanceMeters = Number((gps.totalDistanceMeters + segmentMeters).toFixed(2));

  if (typeof point.altitude === "number" && typeof lastPoint.altitude === "number") {
    const gain = point.altitude - lastPoint.altitude;
    if (gain > 1) {
      gps.totalElevationGain = Number((gps.totalElevationGain + gain).toFixed(1));
    }
  }
}

function createOutdoorGpsState() {
  return {
    source: "gps",
    status: "GPS 已连接",
    watchId: null,
    points: [],
    totalDistanceMeters: 0,
    totalElevationGain: 0,
    lastAccuracy: 0
  };
}

function pauseOutdoorGpsTracking(gpsState = null) {
  const gps = gpsState || state.workoutSession?.gps;
  const watchId = gps?.watchId;
  if (watchId != null && navigator.geolocation?.clearWatch) {
    navigator.geolocation.clearWatch(watchId);
    gps.watchId = null;
  }
}

function stopOutdoorGpsTracking(gpsState = null) {
  pauseOutdoorGpsTracking(gpsState);
}

function getCurrentGeoPosition(options) {
  return new Promise((resolve, reject) => {
    navigator.geolocation.getCurrentPosition(resolve, reject, options);
  });
}

async function startOutdoorGpsTracking(sportId) {
  if (!navigator.geolocation) {
    throw new Error("当前浏览器不支持定位，户外运动暂时无法记录真实轨迹。");
  }

  const initialPosition = await getCurrentGeoPosition({
    enableHighAccuracy: true,
    timeout: 15000,
    maximumAge: 0
  }).catch((error) => {
    throw new Error(getGeoPositionErrorMessage(error));
  });

  const gps = createOutdoorGpsState();

  appendWorkoutGeoPoint(initialPosition, sportId, gps);

  gps.watchId = navigator.geolocation.watchPosition(
    (position) => {
      appendWorkoutGeoPoint(position, sportId);
    },
    (error) => {
      const errorMessage = getGeoPositionErrorMessage(error);
      gps.status = errorMessage;
      if (state.workoutSession?.gps) {
        state.workoutSession.gps.status = errorMessage;
        renderPage();
      }
    },
    {
      enableHighAccuracy: true,
      maximumAge: 0,
      timeout: 20000
    }
  );

  return gps;
}

async function resumeOutdoorGpsTracking(sportId, existingGps = null) {
  if (!navigator.geolocation) {
    throw new Error("当前浏览器不支持定位，户外运动暂时无法记录真实轨迹。");
  }

  const gps = existingGps || createOutdoorGpsState();
  pauseOutdoorGpsTracking(gps);

  const initialPosition = await getCurrentGeoPosition({
    enableHighAccuracy: true,
    timeout: 12000,
    maximumAge: 0
  }).catch(() => null);

  if (initialPosition) {
    appendWorkoutGeoPoint(initialPosition, sportId, gps);
  } else if (!gps.points.length) {
    gps.status = "GPS 正在连接";
  }

  gps.watchId = navigator.geolocation.watchPosition(
    (position) => {
      appendWorkoutGeoPoint(position, sportId, gps);
    },
    (error) => {
      const errorMessage = getGeoPositionErrorMessage(error);
      gps.status = errorMessage;
      if (state.workoutSession?.gps) {
        state.workoutSession.gps.status = errorMessage;
        renderPage();
      }
    },
    {
      enableHighAccuracy: true,
      maximumAge: 0,
      timeout: 20000
    }
  );

  return gps;
}

function getSeedFromText(value) {
  return String(value || "")
    .split("")
    .reduce((sum, char, index) => sum + char.charCodeAt(0) * (index + 3), 0);
}

function getSeededOffset(seed, index, amplitude) {
  const wave = Math.sin(seed * 0.17 + index * 1.73) + Math.cos(seed * 0.11 + index * 1.21);
  return Number((wave * amplitude).toFixed(2));
}

function buildOutdoorRoutePoints(sportId, seed) {
  const template = OUTDOOR_ROUTE_TEMPLATES[sportId] || OUTDOOR_ROUTE_TEMPLATES.run;
  return template.map(([x, y], index) => [
    clampNumber(x + getSeededOffset(seed, index, 2.1), 6, 94),
    clampNumber(y + getSeededOffset(seed + 13, index, 2.6), 18, 88)
  ]);
}

function buildRoutePointsFromGeo(geoPoints) {
  if (!Array.isArray(geoPoints) || !geoPoints.length) return [];
  if (geoPoints.length === 1) return [[50, 52]];

  const lngs = geoPoints.map((item) => item.lng);
  const lats = geoPoints.map((item) => item.lat);
  const minLng = Math.min(...lngs);
  const maxLng = Math.max(...lngs);
  const minLat = Math.min(...lats);
  const maxLat = Math.max(...lats);
  const lngSpan = Math.max(maxLng - minLng, 0.0008);
  const latSpan = Math.max(maxLat - minLat, 0.0008);

  return geoPoints.map((item) => {
    const x = 10 + ((item.lng - minLng) / lngSpan) * 80;
    const y = 84 - ((item.lat - minLat) / latSpan) * 60;
    return [Number(x.toFixed(2)), Number(y.toFixed(2))];
  });
}

function buildRouteCheckpointsFromPoints(points, desiredCount) {
  if (!points.length) return [];
  const checkpointCount = clampNumber(desiredCount, 2, 12);
  return Array.from({ length: checkpointCount }, (_, index) => {
    const ratio = (index + 1) / (checkpointCount + 1);
    const pointIndex = clampNumber(Math.round(ratio * (points.length - 1)), 0, points.length - 1);
    const point = points[pointIndex] || points[points.length - 1];
    return {
      label: String(index + 1),
      x: point[0],
      y: point[1]
    };
  });
}

function buildOutdoorRoutePayload(profile, session) {
  if (!profile || !session || !supportsOutdoorRouteShare(session.sport.id)) return null;

  const geoPoints = Array.isArray(session.gps?.points) ? session.gps.points : [];
  const routePoints = buildRoutePointsFromGeo(geoPoints);

  if (geoPoints.length >= 1 && routePoints.length >= 1) {
    const checkpointCount = clampNumber(Math.round(Math.max(session.distance || 1, 2)), 3, 12);
    const checkpoints = routePoints.length >= 2 ? buildRouteCheckpointsFromPoints(routePoints, checkpointCount) : [];
    const restingHeartRate = Number(profile.restingHeartRate || 64) || 64;
    const avgHeartRateOffset =
      session.sport.id === "outdoor-walk"
        ? 42
        : session.sport.id === "outdoor-cycling"
          ? 58
          : session.sport.id === "hiking"
            ? 52
            : session.sport.id === "trail-run"
              ? 72
              : 66;
    const avgHeartRate = Math.round(restingHeartRate + avgHeartRateOffset);
    const bestPaceSeconds = session.distance
      ? Math.max(
          205,
          Math.round((session.elapsedMinutes * 60) / session.distance * (session.sport.id === "outdoor-walk" ? 0.93 : 0.86))
        )
      : 0;
    const bestPaceLabel = bestPaceSeconds
      ? `${Math.floor(bestPaceSeconds / 60)}'${String(bestPaceSeconds % 60).padStart(2, "0")}"`
      : "--";

    return {
      source: "gps",
      city: profile.city || state.userPosition.city,
      district: profile.locationLabel || state.userPosition.label,
      shareTitle: `${profile.city || state.userPosition.city}市 ${session.sport.label}`,
      startedAt: new Date(session.startedAt).toISOString(),
      dateLabel: formatShareDateLabel(session.startedAt),
      durationLabel: formatWorkoutDurationLabel(session.elapsedSeconds),
      distanceKm: Number((session.distance || 0).toFixed(2)),
      avgPaceLabel: formatWorkoutPaceLabel(session.elapsedMinutes, session.distance),
      bestPaceLabel,
      avgHeartRate,
      elevationGain: Math.round(session.gps?.totalElevationGain || 0),
      calories: session.calories,
      points: routePoints,
      checkpoints,
      geoPoints: geoPoints.map((item) => ({
        lat: item.lat,
        lng: item.lng,
        accuracy: item.accuracy || 0,
        altitude: item.altitude,
        recordedAt: item.recordedAt
      }))
    };
  }
  return null;
}

function getProfileWeight(profile) {
  return Number(profile?.weightKg || 0);
}

function getProfileHeight(profile) {
  return Number(profile?.heightCm || 0);
}

function clampNumber(value, min, max) {
  return Math.min(max, Math.max(min, value));
}

function getProfileBMIRaw(profile) {
  const heightCm = getProfileHeight(profile);
  const weightKg = getProfileWeight(profile);
  if (!heightCm || !weightKg) return 0;
  const heightMeter = heightCm / 100;
  return weightKg / (heightMeter * heightMeter);
}

function getProfileBMI(profile) {
  const bmi = getProfileBMIRaw(profile);
  return bmi ? bmi.toFixed(1) : "--";
}

function getHealthSnapshot(profile) {
  return profile?.healthSnapshot && typeof profile.healthSnapshot === "object"
    ? profile.healthSnapshot
    : {};
}

function getHealthHistory(profile) {
  return Array.isArray(profile?.healthHistory) ? profile.healthHistory : [];
}

function createLocalDateKey(dateInput) {
  const date = getSafeDate(dateInput) || new Date();
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, "0")}-${String(date.getDate()).padStart(2, "0")}`;
}

function getMonthStart(dateInput = new Date()) {
  const date = getSafeDate(dateInput) || new Date();
  return new Date(date.getFullYear(), date.getMonth(), 1);
}

function getMonthEnd(dateInput = new Date()) {
  const date = getSafeDate(dateInput) || new Date();
  return new Date(date.getFullYear(), date.getMonth() + 1, 0);
}

function addDays(dateInput, amount) {
  const date = getSafeDate(dateInput) || new Date();
  const copy = new Date(date);
  copy.setDate(copy.getDate() + amount);
  return copy;
}

function isDateInRange(dateInput, start, end) {
  const date = getSafeDate(dateInput);
  return Boolean(date && start && end && date >= start && date <= end);
}

function formatHealthNumber(value, digits = 1) {
  const numeric = Number(value || 0);
  if (!Number.isFinite(numeric)) return "0";
  if (digits <= 0) return String(Math.round(numeric));
  return numeric.toFixed(digits).replace(/\.0+$/, "").replace(/(\.\d*[1-9])0+$/, "$1");
}

function formatHealthDistance(value) {
  const numeric = Number(value || 0);
  if (!Number.isFinite(numeric) || numeric <= 0) return "0.0";
  return numeric >= 100 ? formatHealthNumber(numeric, 0) : formatHealthNumber(numeric, 1);
}

function formatHealthMinutes(value) {
  const numeric = Math.max(0, Math.round(Number(value || 0)));
  return `${numeric} 分钟`;
}

function formatMonthLabel(dateInput = new Date()) {
  const date = getSafeDate(dateInput) || new Date();
  return `${date.getFullYear()} 年 ${date.getMonth() + 1} 月`;
}

function formatWeekRangeLabel(dateInput = new Date()) {
  const start = getWeekAnchor(dateInput);
  const end = addDays(start, 6);
  return `周报 ${start.getMonth() + 1}.${start.getDate()}-${end.getMonth() + 1}.${end.getDate()}`;
}

function formatShortMonthDay(dateInput) {
  const date = getSafeDate(dateInput);
  if (!date) return "--/--";
  return `${String(date.getMonth() + 1).padStart(2, "0")}/${String(date.getDate()).padStart(2, "0")}`;
}

function getCalendarIntensity(minutes) {
  if (minutes >= 60) return "is-strong";
  if (minutes >= 25) return "is-medium";
  if (minutes > 0) return "is-light";
  return "is-empty";
}

function getCheckinMetricValue(checkin, metric) {
  if (!checkin) return 0;
  if (metric === "distance") return Number(checkin.distance || 0);
  if (metric === "calories") return Number(checkin.calories || 0);
  return Number(checkin.duration || 0);
}

function buildCheckinDayMap(checkins) {
  const daily = new Map();
  for (const checkin of checkins || []) {
    const createdAt = getSafeDate(checkin?.createdAt);
    if (!createdAt) continue;
    const key = createLocalDateKey(createdAt);
    const existing = daily.get(key) || {
      key,
      date: new Date(createdAt.getFullYear(), createdAt.getMonth(), createdAt.getDate()),
      minutes: 0,
      distance: 0,
      calories: 0,
      count: 0,
      sports: new Set()
    };
    existing.minutes += Number(checkin.duration || 0);
    existing.distance += Number(checkin.distance || 0);
    existing.calories += Number(checkin.calories || 0);
    existing.count += 1;
    if (checkin.sportId) existing.sports.add(checkin.sportId);
    daily.set(key, existing);
  }
  return daily;
}

function getDaySummary(dayMap, dateInput) {
  const date = getSafeDate(dateInput);
  if (!date) {
    return { minutes: 0, distance: 0, calories: 0, count: 0, sports: new Set() };
  }
  return dayMap.get(createLocalDateKey(date)) || {
    minutes: 0,
    distance: 0,
    calories: 0,
    count: 0,
    sports: new Set()
  };
}

function getActiveStreakDays(dayMap, fromDate = new Date()) {
  let streak = 0;
  let cursor = new Date(fromDate);
  cursor.setHours(0, 0, 0, 0);
  while (getDaySummary(dayMap, cursor).minutes > 0) {
    streak += 1;
    cursor = addDays(cursor, -1);
  }
  return streak;
}

function buildHealthCalendar(dayMap, focusDate = new Date()) {
  const monthStart = getMonthStart(focusDate);
  const monthEnd = getMonthEnd(focusDate);
  const totalDays = monthEnd.getDate();
  const startOffset = monthStart.getDay();
  const cells = [];

  for (let index = 0; index < startOffset; index += 1) {
    cells.push({ empty: true, id: `empty-${index}` });
  }

  for (let day = 1; day <= totalDays; day += 1) {
    const date = new Date(monthStart.getFullYear(), monthStart.getMonth(), day);
    const summary = getDaySummary(dayMap, date);
    cells.push({
      id: createLocalDateKey(date),
      label: day,
      isToday: isSameLocalDay(date, new Date()),
      minutes: summary.minutes,
      intensity: getCalendarIntensity(summary.minutes)
    });
  }

  return {
    monthLabel: formatMonthLabel(focusDate),
    activeDays: cells.filter((item) => !item.empty && item.minutes > 0).length,
    cells
  };
}

function buildTrailingDaySeries(dayMap, days, field, endDate = new Date()) {
  const series = [];
  for (let offset = days - 1; offset >= 0; offset -= 1) {
    const date = addDays(endDate, -offset);
    const summary = getDaySummary(dayMap, date);
    series.push({
      label: ["日", "一", "二", "三", "四", "五", "六"][date.getDay()],
      value: Number(summary[field] || 0),
      date
    });
  }
  return series;
}

function filterCheckinsInRange(checkins, start, end, sportIds = []) {
  const sportSet = sportIds.length ? new Set(sportIds) : null;
  return (checkins || []).filter((item) => {
    const createdAt = getSafeDate(item.createdAt);
    if (!createdAt || !isDateInRange(createdAt, start, end)) return false;
    return !sportSet || sportSet.has(item.sportId);
  });
}

function buildCumulativeMetricSeries(checkins, sportIds, metric, focusDate = new Date()) {
  const monthStart = getMonthStart(focusDate);
  const monthEnd = getMonthEnd(focusDate);
  const sportSet = new Set(sportIds);
  let runningTotal = 0;
  const series = [];

  for (let day = 1; day <= monthEnd.getDate(); day += 1) {
    const date = new Date(monthStart.getFullYear(), monthStart.getMonth(), day);
    const total = (checkins || []).reduce((sum, item) => {
      const createdAt = getSafeDate(item.createdAt);
      if (!createdAt || !isSameLocalDay(createdAt, date) || !sportSet.has(item.sportId)) {
        return sum;
      }
      return sum + getCheckinMetricValue(item, metric);
    }, 0);
    runningTotal += total;
    series.push({ label: String(day), value: Number(runningTotal.toFixed(metric === "distance" ? 2 : 1)) });
  }

  return series;
}

function buildWeeklyMetricSeries(checkins, sportIds, metric, weeks = 12, focusDate = new Date()) {
  const sportSet = new Set(sportIds);
  const currentWeekStart = getWeekAnchor(focusDate);
  const series = [];

  for (let offset = weeks - 1; offset >= 0; offset -= 1) {
    const weekStart = addDays(currentWeekStart, -offset * 7);
    const weekEnd = addDays(weekStart, 6);
    const total = (checkins || []).reduce((sum, item) => {
      const createdAt = getSafeDate(item.createdAt);
      if (!createdAt || !sportSet.has(item.sportId) || !isDateInRange(createdAt, weekStart, weekEnd)) {
        return sum;
      }
      return sum + getCheckinMetricValue(item, metric);
    }, 0);

    series.push({
      label: `${weekStart.getMonth() + 1}/${weekStart.getDate()}`,
      value: Number(total.toFixed(metric === "distance" ? 2 : 1))
    });
  }

  return series;
}

function parsePaceSeconds(label) {
  const raw = String(label || "");
  const match = raw.match(/(\d+)\s*'\s*(\d{1,2})/);
  if (!match) return 0;
  return Number(match[1]) * 60 + Number(match[2]);
}

function formatPaceSeconds(seconds) {
  const safe = Math.max(0, Math.round(Number(seconds || 0)));
  const minutes = Math.floor(safe / 60);
  const remain = String(safe % 60).padStart(2, "0");
  return `${minutes}'${remain}"`;
}

function renderHealthViewTabs() {
  return `
    <div class="health-view-tabs">
      ${HEALTH_VIEW_MODES.map((item) => `
        <button
          class="health-view-tab ${state.healthViewMode === item.id ? "is-active" : ""}"
          data-set-health-view="${item.id}"
          type="button"
        >
          ${escapeHtml(item.label)}
        </button>
      `).join("")}
    </div>
  `;
}

function renderHealthBarChart(series, options = {}) {
  const { formatter = (value) => String(Math.round(value || 0)), emptyLabel = "暂无数据" } = options;
  const safeSeries = Array.isArray(series) ? series : [];
  const maxValue = Math.max(...safeSeries.map((item) => Number(item.value || 0)), 0);

  if (!safeSeries.length || maxValue <= 0) {
    return `<div class="health-chart-empty">${escapeHtml(emptyLabel)}</div>`;
  }

  return `
    <div class="health-bar-chart">
      ${safeSeries
        .map((item) => {
          const barHeight = Math.max(12, Math.round((Number(item.value || 0) / maxValue) * 100));
          return `
            <div class="health-bar-chart__item">
              <span class="health-bar-chart__value">${escapeHtml(formatter(item.value || 0))}</span>
              <span class="health-bar-chart__track">
                <i style="height:${barHeight}%"></i>
              </span>
              <span class="health-bar-chart__label">${escapeHtml(item.label || "")}</span>
            </div>
          `;
        })
        .join("")}
    </div>
  `;
}

function buildSparklineGeometry(series, width = 320, height = 136, padding = 14) {
  const safeSeries = Array.isArray(series) ? series : [];
  const values = safeSeries.map((item) => Number(item.value || 0));
  const maxValue = Math.max(...values, 0);
  if (!safeSeries.length || maxValue <= 0) return null;

  const usableWidth = width - padding * 2;
  const usableHeight = height - padding * 2;
  const step = safeSeries.length > 1 ? usableWidth / (safeSeries.length - 1) : 0;
  const points = safeSeries.map((item, index) => {
    const x = padding + step * index;
    const y = padding + usableHeight - (Number(item.value || 0) / maxValue) * usableHeight;
    return { x, y };
  });

  const linePath = points
    .map((point, index) => `${index === 0 ? "M" : "L"} ${point.x.toFixed(1)} ${point.y.toFixed(1)}`)
    .join(" ");
  const areaPath = `${linePath} L ${points[points.length - 1].x.toFixed(1)} ${(height - padding).toFixed(1)} L ${points[0].x.toFixed(1)} ${(height - padding).toFixed(1)} Z`;

  return { width, height, padding, points, linePath, areaPath };
}

function renderHealthSparkline(series, options = {}) {
  const { emptyLabel = "暂无数据" } = options;
  const geometry = buildSparklineGeometry(series);
  if (!geometry) {
    return `<div class="health-chart-empty health-chart-empty--wide">${escapeHtml(emptyLabel)}</div>`;
  }

  return `
    <div class="health-sparkline">
      <svg viewBox="0 0 ${geometry.width} ${geometry.height}" aria-hidden="true" focusable="false">
        <path class="health-sparkline__area" d="${geometry.areaPath}"></path>
        <path class="health-sparkline__line" d="${geometry.linePath}"></path>
        ${geometry.points
          .map(
            (point, index) => `
              <circle
                class="health-sparkline__dot ${index === geometry.points.length - 1 ? "is-last" : ""}"
                cx="${point.x.toFixed(1)}"
                cy="${point.y.toFixed(1)}"
                r="${index === geometry.points.length - 1 ? 4.5 : 3}"
              ></circle>
            `
          )
          .join("")}
      </svg>
      <div class="health-sparkline__axis">
        <span>${escapeHtml(series[0]?.label || "")}</span>
        <span>${escapeHtml(series[Math.floor(series.length / 2)]?.label || "")}</span>
        <span>${escapeHtml(series[series.length - 1]?.label || "")}</span>
      </div>
    </div>
  `;
}

function renderHealthCalendar(calendar) {
  return `
    <div class="health-calendar">
      <div class="health-calendar__header">
        <strong>${escapeHtml(calendar.monthLabel)}</strong>
        <span>${calendar.activeDays} 个活跃日</span>
      </div>
      <div class="health-calendar__weekdays">
        ${["日", "一", "二", "三", "四", "五", "六"].map((label) => `<span>${label}</span>`).join("")}
      </div>
      <div class="health-calendar__grid">
        ${calendar.cells
          .map((cell) => {
            if (cell.empty) {
              return '<span class="health-calendar__cell health-calendar__cell--empty"></span>';
            }
            return `
              <span class="health-calendar__cell ${cell.isToday ? "is-today" : ""}">
                <span class="health-calendar__day">${cell.label}</span>
                <i class="health-calendar__dot ${cell.intensity}"></i>
              </span>
            `;
          })
          .join("")}
      </div>
    </div>
  `;
}

function renderRunPaceRows(items) {
  const safeItems = Array.isArray(items) ? items.filter((item) => item.seconds > 0) : [];
  if (!safeItems.length) {
    return '<div class="health-chart-empty">最近 5 次跑步的配速会显示在这里</div>';
  }

  const slowest = Math.max(...safeItems.map((item) => item.seconds));
  const fastest = Math.min(...safeItems.map((item) => item.seconds));
  const range = Math.max(1, slowest - fastest);

  return `
    <div class="health-pace-list">
      ${safeItems
        .map((item) => {
          const width = 42 + ((slowest - item.seconds) / range) * 50;
          return `
            <div class="health-pace-row">
              <span class="health-pace-row__date">${escapeHtml(formatShortMonthDay(item.createdAt))}</span>
              <span class="health-pace-row__track">
                <i style="width:${width.toFixed(1)}%"></i>
              </span>
              <strong class="${item.isFastest ? "is-highlight" : ""}">${escapeHtml(item.label)}</strong>
            </div>
          `;
        })
        .join("")}
    </div>
  `;
}

function getComparisonLabel(todayValue, yesterdayValue) {
  const today = Math.round(Number(todayValue || 0));
  const yesterday = Math.round(Number(yesterdayValue || 0));
  if (!today && !yesterday) return "今天到目前为止，还没有新的训练记录。";
  if (today === yesterday) return "今天到目前为止，运动时长和昨天一样。";
  if (today > yesterday) return `今天到目前为止，比昨天多运动 ${today - yesterday} 分钟。`;
  return `今天到目前为止，比昨天少运动 ${yesterday - today} 分钟。`;
}

function buildHealthDashboard(profile) {
  const checkins = getProfileCheckins(profile);
  const dayMap = buildCheckinDayMap(checkins);
  const today = new Date();
  const monthStart = getMonthStart(today);
  const monthEnd = getMonthEnd(today);
  const previousMonthStart = new Date(today.getFullYear(), today.getMonth() - 1, 1);
  const previousMonthEnd = new Date(today.getFullYear(), today.getMonth(), 0);
  const currentMonthCheckins = filterCheckinsInRange(checkins, monthStart, monthEnd);
  const previousMonthCheckins = filterCheckinsInRange(checkins, previousMonthStart, previousMonthEnd);
  const todaySummary = getDaySummary(dayMap, today);
  const yesterdaySummary = getDaySummary(dayMap, addDays(today, -1));
  const sevenDaySeries = buildTrailingDaySeries(dayMap, 7, "minutes", today);
  const sevenDayAverage = sevenDaySeries.reduce((sum, item) => sum + Number(item.value || 0), 0) / 7;
  const sevenDayTotal = sevenDaySeries.reduce((sum, item) => sum + Number(item.value || 0), 0);
  const snapshot = getHealthSnapshot(profile);
  const connectedDevices = getConnectedDevices(profile);
  const sortedHealthHistory = getHealthHistory(profile)
    .filter((item) => item && item.date)
    .slice()
    .sort((left, right) => new Date(left.date) - new Date(right.date));
  let stepHistory = sortedHealthHistory.slice(-7).map((item) => ({
    label: formatShortMonthDay(item.date),
    value: Number(item.stepCount || 0),
    date: item.date
  }));
  const todayKey = createLocalDateKey(today);
  const snapshotStepCount = Number(snapshot.stepCount || 0);
  if (snapshotStepCount > 0) {
    const todayHistory = stepHistory.find((item) => item.date === todayKey);
    if (todayHistory) {
      todayHistory.value = Math.max(todayHistory.value, snapshotStepCount);
    } else {
      stepHistory = [...stepHistory, {
        label: formatShortMonthDay(today),
        value: snapshotStepCount,
        date: todayKey
      }].slice(-7);
    }
  }
  const todaySteps = Number(snapshot.stepCount || stepHistory[stepHistory.length - 1]?.value || 0);
  const yesterdaySteps = stepHistory.length >= 2 ? Number(stepHistory[stepHistory.length - 2].value || 0) : 0;
  const recentRuns = checkins
    .filter((item) => ["run", "treadmill", "trail-run"].includes(item.sportId) && parsePaceSeconds(item.paceLabel) > 0)
    .slice(0, 5)
    .map((item) => ({
      createdAt: item.createdAt,
      seconds: parsePaceSeconds(item.paceLabel),
      label: item.paceLabel
    }));
  const fastestRun = recentRuns.length ? Math.min(...recentRuns.map((item) => item.seconds)) : 0;
  const runPaceRows = recentRuns.map((item) => ({
    ...item,
    isFastest: item.seconds === fastestRun
  }));

  const sportCards = HEALTH_TREND_GROUPS.map((group) => {
    const monthItems = filterCheckinsInRange(checkins, monthStart, monthEnd, group.sportIds);
    const previousMonthItems = filterCheckinsInRange(checkins, previousMonthStart, previousMonthEnd, group.sportIds);
    const monthTotal = monthItems.reduce((sum, item) => sum + getCheckinMetricValue(item, group.metric), 0);
    const previousMonthTotal = previousMonthItems.reduce((sum, item) => sum + getCheckinMetricValue(item, group.metric), 0);
    const series =
      group.id === "yoga"
        ? buildWeeklyMetricSeries(checkins, group.sportIds, group.metric, 12, today)
        : buildCumulativeMetricSeries(checkins, group.sportIds, group.metric, today);

    return {
      ...group,
      monthTotal,
      previousMonthTotal,
      totalLabel: `${formatHealthNumber(monthTotal, group.metric === "distance" ? 1 : 0)} ${group.unit}`,
      compareLabel:
        previousMonthTotal > 0
          ? `较上月 ${monthTotal >= previousMonthTotal ? "提升" : "回落"} ${formatHealthNumber(Math.abs(monthTotal - previousMonthTotal), group.metric === "distance" ? 1 : 0)} ${group.unit}`
          : `本月截至目前，暂未形成完整 ${group.label} 趋势`,
      series
    };
  });

  const vo2Value = Number(snapshot.vo2Max || snapshot.maxOxygenUptake || snapshot.cardioFitness || 0);
  const activeEnergy = Number(snapshot.activeEnergyBurned || todaySummary.calories || 0);

  return {
    weekLabel: formatWeekRangeLabel(today),
    calendar: buildHealthCalendar(dayMap, today),
    monthActiveDays: currentMonthCheckins.length
      ? new Set(currentMonthCheckins.map((item) => createLocalDateKey(item.createdAt))).size
      : 0,
    streakDays: getActiveStreakDays(dayMap, today),
    monthMinutes: currentMonthCheckins.reduce((sum, item) => sum + Number(item.duration || 0), 0),
    monthCalories: currentMonthCheckins.reduce((sum, item) => sum + Number(item.calories || 0), 0),
    monthDistance: currentMonthCheckins.reduce((sum, item) => sum + Number(item.distance || 0), 0),
    todayMinutes: todaySummary.minutes,
    yesterdayMinutes: yesterdaySummary.minutes,
    comparisonLabel: getComparisonLabel(todaySummary.minutes, yesterdaySummary.minutes),
    sevenDayTotal,
    sevenDayAverage,
    sevenDaySeries,
    bodyMetrics: [
      { label: "BMI", value: getProfileBMI(profile), note: "身体质量指数" },
      { label: "体脂率", value: profile.bodyFat ? `${formatHealthNumber(profile.bodyFat, 1)}%` : "--", note: "最近一次体脂" },
      { label: "静息心率", value: profile.restingHeartRate ? `${Math.round(Number(profile.restingHeartRate))} bpm` : "--", note: "设备同步更新" },
      { label: "已连设备", value: connectedDevices.length ? `${connectedDevices.length} 台` : "未连接", note: profile.healthSource || "原生同步" }
    ],
    steps: {
      today: todaySteps,
      yesterday: yesterdaySteps,
      average: stepHistory.length
        ? Math.round(stepHistory.reduce((sum, item) => sum + Number(item.value || 0), 0) / Math.max(1, stepHistory.length))
        : 0,
      series: stepHistory,
      syncedAt: profile.deviceSyncedAt || "",
      source: profile.healthSource || ""
    },
    vo2: {
      value: vo2Value > 0 ? `${formatHealthNumber(vo2Value, 1)}` : "--",
      source: profile.healthSource || "",
      activeEnergy: activeEnergy > 0 ? `${formatHealthNumber(activeEnergy, 0)} kcal` : "--"
    },
    sportCards,
    runPaceRows
  };
}

function getWorkoutSessionStats(profile) {
  return getWorkoutSessionStatsForState(profile, state.workoutSession);
}

function getWorkoutSessionStatsForState(profile, session) {
  if (!session) return null;

  const sport = getCheckinSport(session.sportId);
  const metrics = getCheckinMetrics(session.sportId);
  const calibration = getWorkoutCalibration(profile, metrics);
  const gps = session.gps || null;
  const pauseAnchor = session.pausedAt || Date.now();
  const elapsedSeconds = Math.max(
    0,
    Math.floor((pauseAnchor - session.startedAt - Number(session.pausedDurationMs || 0)) / 1000)
  );
  const elapsedMinutes = Math.max(1, Math.floor(elapsedSeconds / 60));
  const hours = elapsedSeconds / 3600;
  const weightKg = getProfileWeight(profile) || 60;
  const calories = Math.max(
    1,
    Math.round(((metrics.met * 3.5 * weightKg * elapsedMinutes) / 200) * calibration.calorieFactor)
  );
  const gpsDistanceKm = gps?.totalDistanceMeters
    ? Number((gps.totalDistanceMeters / 1000).toFixed(hours >= 1 ? 2 : 3))
    : 0;
  const distance = supportsOutdoorRouteShare(session.sportId)
    ? gpsDistanceKm
    : metrics.paceKmh
      ? Number((metrics.paceKmh * hours * calibration.distanceFactor).toFixed(hours >= 1 ? 1 : 2))
      : 0;
  const sourceLabel = supportsOutdoorRouteShare(session.sportId)
    ? gps?.points?.length >= 2
      ? "已结合实时定位点位与身体数据记录户外轨迹"
      : gps?.status || "正在连接 GPS，连接成功后会开始记录真实轨迹"
    : calibration.sourceLabel;

  return {
    ...session,
    sport,
    elapsedSeconds,
    elapsedMinutes,
    timerLabel: formatWorkoutTimer(elapsedSeconds),
    calories,
    distance,
    sourceLabel
  };
}

function shouldCaptureFinalWorkoutPoint(gpsState) {
  const points = Array.isArray(gpsState?.points) ? gpsState.points : [];
  if (!points.length) return true;
  const lastPoint = points[points.length - 1];
  const lastRecordedAt = new Date(lastPoint?.recordedAt || 0).getTime();
  if (!Number.isFinite(lastRecordedAt) || !lastRecordedAt) return true;
  return Date.now() - lastRecordedAt > 5000 || points.length < 2;
}

async function persistFinishedWorkout({ forceFinalPoint = false } = {}) {
  const draft = state.pendingFinishedWorkout;
  if (!draft?.sessionState || !draft?.profileSnapshot) return;

  const profile = getProfile(draft.profileId) || draft.profileSnapshot;
  const sessionState = draft.sessionState;
  const sport = getCheckinSport(sessionState.sportId);
  const expectsOutdoorRoute = supportsOutdoorRouteShare(sport.id);

  if (
    expectsOutdoorRoute &&
    navigator.geolocation &&
    sessionState.gps &&
    (forceFinalPoint || shouldCaptureFinalWorkoutPoint(sessionState.gps))
  ) {
    const finalPosition = await getCurrentGeoPosition({
      enableHighAccuracy: true,
      timeout: 1800,
      maximumAge: 2000
    }).catch(() => null);

    if (finalPosition) {
      appendWorkoutGeoPoint(finalPosition, sport.id, sessionState.gps);
    }
  }

  const session = getWorkoutSessionStatsForState(profile, sessionState);
  const routePayload = buildOutdoorRoutePayload(profile, session);

  await postAndSync(`${API_BASE}/checkin/create`, {
    profileId: profile.id,
    sportId: session.sport.id,
    sportLabel: session.sport.label,
    duration: session.elapsedMinutes,
    calories: session.calories,
    distance: session.distance,
    paceLabel: routePayload?.avgPaceLabel || "",
    bestPaceLabel: routePayload?.bestPaceLabel || "",
    heartRateAvg: routePayload?.avgHeartRate || 0,
    elevationGain: routePayload?.elevationGain || 0,
    route: routePayload,
    note: "",
    content: routePayload
      ? `完成了一次 ${session.sport.label}，累计 ${routePayload.distanceKm} km，耗时 ${routePayload.durationLabel}，估算消耗 ${session.calories} kcal。`
      : `完成了一次 ${session.sport.label} 训练，持续 ${session.elapsedMinutes} 分钟，估算消耗 ${session.calories} kcal。`
  });

  state.pendingFinishedWorkout = null;
  state.workoutFinishing = null;

  const latestProfile = getProfile(profile.id);
  const latestCheckin = latestProfile?.checkins?.[0];
  if (routePayload && latestCheckin?.route) {
    state.outdoorShareCheckinId = latestCheckin.id;
    state.profileSubpage = "outdoor-share";
    if (appView) appView.scrollTop = 0;
  } else if (expectsOutdoorRoute) {
    showError("这次训练已记录，但没有采集到足够的真实定位点位，所以没有生成轨迹页。请在空旷区域允许持续定位后再试。");
  }
  renderPage();
}

function getProfileCheckins(profile) {
  return [...(profile?.checkins || [])].sort(
    (left, right) => new Date(right.createdAt || 0).getTime() - new Date(left.createdAt || 0).getTime()
  );
}

function getWeeklyCheckins(profile) {
  const weekStart = getWeekAnchor(new Date());
  return getProfileCheckins(profile).filter((item) => {
    const createdAt = getSafeDate(item.createdAt);
    return createdAt && createdAt >= weekStart;
  });
}

function getTodayCheckins(profile) {
  const today = new Date();
  return getProfileCheckins(profile).filter((item) => isSameLocalDay(getSafeDate(item.createdAt), today));
}

function getProfilePoints(profile, bookings = []) {
  const weeklyCheckins = getWeeklyCheckins(profile).length;
  const completedBookings = bookings.filter((item) => ["已预约", "待上课", "已完成"].includes(item.status)).length;
  return weeklyCheckins * 12 + completedBookings * 18;
}

function getManagedDashboardStats(profile) {
  if (!profile) return [];

  if (profile.role === "enthusiast") {
    const stats = getPersonalDashboard(profile);
    return [
      { value: stats.trainingScore, label: "练时" },
      { value: stats.todayTraining, label: "今日训练" },
      { value: stats.badges, label: "勋章" }
    ];
  }

  const incomingBookings = getIncomingBookings(profile);
  const pendingCount = incomingBookings.filter((item) => ["待上课", "待确认", "已预约"].includes(item.status)).length;
  const todayOrders = incomingBookings.filter((item) => isSameLocalDay(getSafeDate(item.createdAt), new Date())).length;
  const ratingValue = profile.ratingCount ? getRatingDisplay(profile) : "新入驻";

  return [
    { value: String(pendingCount), label: profile.role === "coach" ? "待上课" : "待到店" },
    { value: String(todayOrders), label: "今日预约" },
    { value: ratingValue, label: "评分" }
  ];
}

function getPersonalDashboard(profile) {
  const checkins = getProfileCheckins(profile);
  const todayCheckins = getTodayCheckins(profile);
  const totalMinutes = checkins.reduce((sum, item) => sum + Number(item.duration || 0), 0);
  const badgeCount =
    (checkins.length >= 1 ? 1 : 0) +
    (checkins.length >= 3 ? 1 : 0) +
    (checkins.length >= 7 ? 1 : 0) +
    (totalMinutes >= 300 ? 1 : 0);

  return {
    trainingScore: totalMinutes ? (totalMinutes / 60).toFixed(totalMinutes >= 600 ? 0 : 1) : "0",
    todayTraining: String(todayCheckins.length),
    badges: String(badgeCount)
  };
}

function getBookingDashboard(profile) {
  const bookings = getRelevantBookingsForProfile(profile);
  const pendingLabel = profile?.role === "enthusiast" ? "本周待上课" : profile?.role === "coach" ? "待上课" : "待到店";
  return {
    pendingLabel,
    pendingCount: bookings.filter((item) => ["待上课", "待确认", "已预约"].includes(item.status)).length,
    weeklyCheckins: getWeeklyCheckins(profile).length,
    points: getProfilePoints(profile, bookings)
  };
}

function renderPersonalShortcutTile(label, sublabel, icon, attrs = "") {
  return `
    <button class="account-tile" type="button" ${attrs}>
      <span class="account-tile-icon">${escapeHtml(icon)}</span>
      <strong>${escapeHtml(label)}</strong>
    </button>
  `;
}

function renderSocialTabs(activeTab) {
  return `
    <div class="social-tabs">
      <button class="social-tab ${activeTab === "following" ? "is-active" : ""}" data-set-social-tab="following" type="button">
        我关注的
      </button>
      <button class="social-tab ${activeTab === "followers" ? "is-active" : ""}" data-set-social-tab="followers" type="button">
        我的粉丝
      </button>
    </div>
  `;
}

function renderSocialProfilesSection(mode = "following") {
  const profiles = mode === "followers" ? getFollowerProfiles() : getFollowedProfiles();
  const emptyText =
    mode === "followers"
      ? "你还没有新的粉丝，继续发布动态、完善主页和接收预约后，这里会慢慢热闹起来。"
      : "你还没有关注任何对象，先去探索页点几个感兴趣的人或场馆吧。";

  return `
    ${renderSocialTabs(mode)}
    <section class="feature-follow-list">
      ${
        profiles.length
          ? profiles
              .map(
                (item) => `
                  <article class="feature-follow-item">
                    <button class="feature-follow-main" data-open-profile="${item.id}" type="button">
                      ${renderAvatarMarkup(item, "avatar")}
                      <div>
                        <strong>${escapeHtml(item.name)}</strong>
                        <p>${escapeHtml(getRoleLabel(item.role))} · ${escapeHtml(item.locationLabel || item.city || "未填写位置")}</p>
                      </div>
                    </button>
                    ${
                      mode === "followers"
                        ? state.followSet.has(item.id)
                          ? '<button class="follow-button is-reciprocal" type="button" disabled>已回关</button>'
                          : `<button class="follow-button following-action" data-follow-back="${item.id}" type="button">回关</button>`
                        : ""
                    }
                  </article>
                `
              )
              .join("")
          : `<article class="empty-card">${emptyText}</article>`
      }
    </section>
  `;
}

function renderManagedBookingList(profile, bookings, { emptyText = "", primaryAction = "查看主页" } = {}) {
  const profileRole = profile?.role || "enthusiast";
  if (!bookings.length) {
    return `<article class="empty-card">${emptyText}</article>`;
  }

  return `
    <section class="stack-list">
      ${bookings
        .map((card) => {
          const counterpartLabel = card.counterpartProfileName || card.targetProfileName || "平台用户";
          const counterpartRole = getRoleLabel(card.counterpartProfileRole || "");
          const metaLeft = profileRole === "enthusiast"
            ? `${counterpartLabel} · ${counterpartRole || "服务方"}`
            : `${counterpartLabel} · ${counterpartRole || "预约人"}`;
          return `
            <article class="booking-card">
              <div class="booking-top">
                <strong>${escapeHtml(card.title || `${counterpartLabel} · 预约记录`)}</strong>
                <span class="status-pill">${escapeHtml(card.status || "待确认")}</span>
              </div>
              <p>${escapeHtml(metaLeft)}</p>
              <div class="community-meta">
                <span>${escapeHtml(card.price || "待确认")}</span>
                <span>${escapeHtml(card.time || "待确认")}</span>
              </div>
              <div class="booking-bottom">
                <span>${escapeHtml(card.place || card.counterpartLocationLabel || "位置待确认")}</span>
                <button class="cta" type="button" data-open-profile="${card.counterpartProfileId || card.targetProfileId || card.createdByProfileId || ""}">
                  ${escapeHtml(primaryAction)}
                </button>
              </div>
            </article>
          `;
        })
        .join("")}
    </section>
  `;
}

function renderMessagesFeature(profile) {
  const notifications = Array.isArray(state.notifications) ? state.notifications : [];
  const threads = (state.threads || []).filter(Boolean);
  const notificationsSeenAt = new Date(getActorMessageReadState().notificationsSeenAt || 0).getTime() || 0;
  if (!notifications.length && !threads.length) {
    return '<article class="empty-card">还没有新的互动消息。别人给你的赞、评论、@和私信会集中显示在这里。</article>';
  }

  return `
    <section class="stack-list">
      ${
        notifications.length
          ? `
            <article class="detail-card">
              <div class="section-title-row">
                <div>
                  <h3>互动消息</h3>
                  <p class="result-tip">集中查看别人给你的赞、评论和 @ 你的内容。</p>
                </div>
              </div>
              <section class="stack-list">
                ${notifications
                  .map(
                    (item) => `
                      <article class="feature-follow-item">
                        <button class="feature-follow-main" data-open-profile="${item.actorProfileId}" type="button">
                          ${renderAvatarMarkup({ name: item.actorName, avatarImage: item.actorAvatarImage, role: item.actorRole || "enthusiast", unreadCount: new Date(item.createdAt || 0).getTime() > notificationsSeenAt ? 1 : 0 }, "avatar")}
                          <div>
                            <strong>${escapeHtml(item.actorName)}</strong>
                            <p>${escapeHtml(item.text)}</p>
                            <small>${escapeHtml(item.time)}</small>
                          </div>
                        </button>
                        <span class="status-pill status-pill--soft">${escapeHtml(item.type === "like" ? "赞" : item.type === "comment" ? "评论" : "@我")}</span>
                      </article>
                    `
                  )
                  .join("")}
              </section>
            </article>
          `
          : ""
      }
      ${
        threads.length
          ? `
            <article class="detail-card">
              <div class="section-title-row">
                <div>
                  <h3>私信咨询</h3>
                  <p class="result-tip">已关注后可继续沟通预约、课程和训练安排。</p>
                </div>
              </div>
              <section class="stack-list">
                ${threads
                  .map(
                    (thread) => `
                      <article class="feature-follow-item">
                        <button class="feature-follow-main" data-open-chat="${thread.withProfileId}" type="button">
                          ${renderAvatarMarkup({ name: thread.withProfileName, avatarImage: thread.withProfileAvatarImage, role: "enthusiast", unreadCount: getThreadUnreadCount(thread) }, "avatar")}
                          <div>
                            <strong>${escapeHtml(thread.withProfileName)}</strong>
                            <p>${escapeHtml(thread.lastMessage?.text || "打开查看最新消息")}</p>
                            <small>${escapeHtml(thread.lastMessage?.time || "刚刚")}</small>
                          </div>
                        </button>
                      </article>
                    `
                  )
                  .join("")}
              </section>
            </article>
          `
          : ""
      }
    </section>
  `;
}

function renderCollectionsFeature() {
  const entries = getFavoritedMediaEntries();
  if (!entries.length) {
    return '<article class="empty-card">你还没有收藏任何图片或视频。看到喜欢的动作讲解、训练视频或照片时，点一下星标就会收进这里。</article>';
  }

  return `
    <section class="timeline-list">
      ${entries.map(({ profile, post }) => renderPostCard(profile, post)).join("")}
    </section>
  `;
}

function renderReviewsFeature(profile) {
  if (profile.role === "enthusiast") {
    return `
      <article class="detail-card">
        <p class="result-tip">当前训练者身份不展示公开评分，继续打卡和互动会沉淀到你的主页与动态。</p>
      </article>
    `;
  }

  const reviews = Array.isArray(profile.reviews) ? profile.reviews : [];
  return `
    <article class="detail-card">
      <div class="section-title-row">
        <div>
          <h3>${profile.role === "coach" ? "学员评分" : "场馆评分"}</h3>
          <p class="result-tip">${profile.ratingCount ? `当前平均 ${getRatingDisplay(profile)} 分，共 ${profile.ratingCount} 条评分。` : "现在还没有用户评分，完成第一笔预约后这里会开始积累评价。"}</p>
        </div>
      </div>
      ${
        reviews.length
          ? `
              <section class="review-list">
                ${reviews
                  .map(
                    (review) => `
                      <article class="review-card detail-card">
                        <div class="review-head">
                          <strong>${escapeHtml(review.author || "平台用户")}</strong>
                          <span>${escapeHtml(`${review.score} 星 · ${review.time}`)}</span>
                        </div>
                        <p>${escapeHtml(review.text || "刚刚完成一次评分。")}</p>
                      </article>
                    `
                  )
                  .join("")}
              </section>
            `
          : '<article class="empty-card">还没有新的评分，先让用户完成一次预约和训练体验吧。</article>'
      }
    </article>
  `;
}

function getFavoriteSports(profile) {
  const favoriteIds = profile?.favoriteSports || [];
  return favoriteIds.map((itemId) => findCheckinSport(itemId)).filter(Boolean);
}

function getCurrentWorkoutSport(profile) {
  const favoriteSports = getFavoriteSports(profile);
  if (!favoriteSports.length) return null;
  const activeSport = favoriteSports.find((item) => item.id === state.checkinCurrentSportId);
  return activeSport || favoriteSports[0];
}

function getConnectedDevices(profile) {
  return profile?.connectedDevices || [];
}

function getWorkoutDeviceSummary(profile) {
  const devices = getConnectedDevices(profile);
  if (!devices.length) return "未连接设备";
  return devices.join(" · ");
}

function hasConnectedWatch(profile) {
  return getConnectedDevices(profile).some((item) => /watch|手表/i.test(item));
}

function hasConnectedScale(profile) {
  return getConnectedDevices(profile).some((item) => /秤/i.test(item));
}

function getWorkoutCalibration(profile, metrics) {
  const bmi = getProfileBMIRaw(profile);
  const bodyFat = Number(profile?.bodyFat || 0);
  const heightFactor = getProfileHeight(profile)
    ? clampNumber(getProfileHeight(profile) / 170, 0.92, 1.08)
    : 1;
  const impactRatio = {
    high: 0.014,
    mixed: 0.01,
    low: 0.006,
    water: 0.004
  }[metrics.impact || "mixed"];
  const bmiFactor = bmi ? 1 + clampNumber((bmi - 22) * impactRatio, -0.06, 0.14) : 1;
  const bodyFatFactor = bodyFat ? 1 + clampNumber((bodyFat - 20) * 0.0025, -0.03, 0.06) : 1;
  const watchFactor = hasConnectedWatch(profile) ? 1.02 : 1;
  const scaleFactor = hasConnectedScale(profile) ? 1.01 : 1;

  return {
    calorieFactor: clampNumber(bmiFactor * bodyFatFactor * watchFactor * scaleFactor, 0.85, 1.24),
    distanceFactor: clampNumber(heightFactor * (hasConnectedWatch(profile) ? 1.02 : 1), 0.9, 1.12),
    sourceLabel: hasConnectedWatch(profile)
      ? "已结合手表与身体数据估算"
      : hasConnectedScale(profile)
        ? "已结合智能秤与身体数据估算"
        : "按运动类型与身体数据估算"
  };
}

function getSportPickerSections(selectedIds = []) {
  const selectedSet = new Set(selectedIds);
  const favorites = selectedIds.map((sportId) => findCheckinSport(sportId)).filter(Boolean);
  const sections = [];

  if (favorites.length) {
    sections.push({ label: "常用运动", sports: favorites });
  }

  CHECKIN_SPORT_SECTIONS.forEach((section) => {
    const sports = section.ids
      .map((sportId) => findCheckinSport(sportId))
      .filter((sport) => sport && !selectedSet.has(sport.id));
    if (sports.length) {
      sections.push({ label: section.label, sports });
    }
  });

  return sections;
}

function renderCheckinEntry(profile) {
  const activeSession = getWorkoutSessionStats(profile);
  const weeklyCount = getWeeklyCheckins(profile).length;
  const favoriteSports = getFavoriteSports(profile);
  const currentSport = getCurrentWorkoutSport(profile);
  const hasSelection = Boolean(currentSport);

  return `
    <article class="dashboard-checkin dashboard-checkin--go">
      <div class="dashboard-checkin-head">
        <span class="dashboard-checkin-kicker">本周打卡 ${weeklyCount} 次</span>
        <button class="text-link" data-open-my-feature="checkin" type="button">管理</button>
      </div>
      <div class="dashboard-checkin-pills dashboard-checkin-pills--toolbar">
        ${
          favoriteSports.length
            ? favoriteSports
                .slice(0, 4)
                .map(
                  (item) => `
                    <button
                      class="workout-type-chip ${item.id === currentSport.id ? "is-active" : ""}"
                      data-select-workout-sport="${item.id}"
                      type="button"
                    >
                      ${escapeHtml(item.label)}
                    </button>
                  `
                )
                .join("")
            : '<button class="workout-type-chip is-empty" data-open-my-feature="checkin" type="button">选择运动</button>'
        }
      </div>
      <div class="dashboard-go-row">
        <div class="dashboard-go-copy">
          <strong>${escapeHtml(activeSession ? activeSession.sport.label : hasSelection ? currentSport.label : "先选择运动")}</strong>
          <p>${
            activeSession
              ? escapeHtml(`${activeSession.timerLabel} · ${activeSession.calories} kcal${activeSession.distance ? ` · ${activeSession.distance} km` : ""}`)
              : escapeHtml(hasSelection ? getWorkoutDeviceSummary(profile) : "第一次打卡先选日常训练项目，再开始计时")
          }</p>
        </div>
        ${
          activeSession
            ? '<button class="dashboard-go-button dashboard-go-button--live" data-open-my-feature="checkin" type="button">继续</button>'
            : `
                <button class="dashboard-go-button" ${hasSelection ? 'data-go-workout="1"' : 'data-open-my-feature="checkin"'} type="button">
                  ${hasSelection ? "运动 GO" : "先选择"}
                </button>
              `
        }
      </div>
    </article>
  `;
}

function renderPersonalMoments(profile) {
  const posts = profile.posts || [];
  return `
    <section class="moments-list">
      ${
        posts.length
          ? posts
              .map(
                (post) => `
                  <article class="moment-card">
                    <div class="moment-card-head">
                      <div>
                        <strong>${escapeHtml(post.meta || "训练动态")}</strong>
                        <span>${escapeHtml(post.time)}</span>
                      </div>
                      ${
                        post.checkin?.route && supportsOutdoorRouteShare(post.checkin?.sportId)
                          ? `<button class="text-link" data-open-route-map-detail="${post.checkin.id}" type="button">查看轨迹</button>`
                          : `<button class="text-link" data-open-profile="${profile.id}" type="button">查看</button>`
                      }
                    </div>
                    <p>${escapeHtml(post.content)}</p>
                    ${renderPostMedia(post)}
                    <div class="moment-card-foot">
                      <span>${escapeHtml(profile.locationLabel)}</span>
                      <span>${post.likeCount || 0} 赞 · ${(post.comments || []).length} 评论</span>
                    </div>
                  </article>
                `
              )
              .join("")
          : '<article class="empty-card">你还没有发布动态。完成一次打卡，或点底部 + 发布第一条健身圈记录。</article>'
      }
    </section>
  `;
}

function renderCheckinHistory(profile) {
  const recentCheckins = getProfileCheckins(profile).slice(0, 3);

  if (!recentCheckins.length) {
    return '<article class="empty-card">这周还没有打卡记录。先完成一次训练，系统会自动生成第一条打卡动态。</article>';
  }

  return `
    <section class="checkin-history-list">
      ${recentCheckins
        .map(
          (item) => `
            <article class="checkin-history-item">
              <div>
                <strong>${escapeHtml(item.sportLabel || "训练打卡")}</strong>
                <p>${escapeHtml(item.note || "已记录到你的训练档案")}</p>
                ${
                  item.route && supportsOutdoorRouteShare(item.sportId)
                    ? `<button class="mini-button mini-button--accent" data-open-route-share="${item.id}" type="button">查看轨迹</button>`
                    : ""
                }
              </div>
              <div class="checkin-history-meta">
                <span>${escapeHtml(item.time || "")}</span>
                <strong>${escapeHtml(`${item.duration || 0} min`)}</strong>
              </div>
            </article>
          `
        )
        .join("")}
    </section>
  `;
}

function getOutdoorShareCheckin(profile) {
  const routeCheckins = getProfileCheckins(profile).filter(
    (item) => item?.route && supportsOutdoorRouteShare(item.sportId)
  );
  if (!routeCheckins.length) return null;
  if (state.outdoorShareCheckinId) {
    return routeCheckins.find((item) => item.id === state.outdoorShareCheckinId) || routeCheckins[0];
  }
  return routeCheckins[0];
}

function canRenderAmapRoute(route) {
  const config = getEffectiveRuntimeConfig();
  return (
    config.mapProvider === "amap" &&
    Boolean(config.amapKey) &&
    Array.isArray(route?.geoPoints) &&
    route.geoPoints.length >= 1
  );
}

function isInsideChina(lng, lat) {
  return lng >= 72.004 && lng <= 137.8347 && lat >= 0.8293 && lat <= 55.8271;
}

function transformLatOffset(lng, lat) {
  let value = -100 + 2 * lng + 3 * lat + 0.2 * lat * lat + 0.1 * lng * lat + 0.2 * Math.sqrt(Math.abs(lng));
  value += ((20 * Math.sin(6 * lng * Math.PI) + 20 * Math.sin(2 * lng * Math.PI)) * 2) / 3;
  value += ((20 * Math.sin(lat * Math.PI) + 40 * Math.sin((lat / 3) * Math.PI)) * 2) / 3;
  value += ((160 * Math.sin((lat / 12) * Math.PI) + 320 * Math.sin((lat * Math.PI) / 30)) * 2) / 3;
  return value;
}

function transformLngOffset(lng, lat) {
  let value = 300 + lng + 2 * lat + 0.1 * lng * lng + 0.1 * lng * lat + 0.1 * Math.sqrt(Math.abs(lng));
  value += ((20 * Math.sin(6 * lng * Math.PI) + 20 * Math.sin(2 * lng * Math.PI)) * 2) / 3;
  value += ((20 * Math.sin(lng * Math.PI) + 40 * Math.sin((lng / 3) * Math.PI)) * 2) / 3;
  value += ((150 * Math.sin((lng / 12) * Math.PI) + 300 * Math.sin((lng / 30) * Math.PI)) * 2) / 3;
  return value;
}

function wgs84ToGcj02(lng, lat) {
  if (!isInsideChina(lng, lat)) return [lng, lat];
  const a = 6378245.0;
  const ee = 0.00669342162296594323;
  let dLat = transformLatOffset(lng - 105.0, lat - 35.0);
  let dLng = transformLngOffset(lng - 105.0, lat - 35.0);
  const radLat = (lat / 180.0) * Math.PI;
  let magic = Math.sin(radLat);
  magic = 1 - ee * magic * magic;
  const sqrtMagic = Math.sqrt(magic);
  dLat = (dLat * 180.0) / (((a * (1 - ee)) / (magic * sqrtMagic)) * Math.PI);
  dLng = (dLng * 180.0) / ((a / sqrtMagic) * Math.cos(radLat) * Math.PI);
  return [lng + dLng, lat + dLat];
}

function getAmapRuntimeConfig() {
  const config = getEffectiveRuntimeConfig();
  if (config.mapProvider !== "amap" || !config.amapKey) return null;
  return config;
}

function registerRouteMap(route, mapId) {
  if (!mapId || !route) return;
  routeMapRegistry.set(mapId, {
    route: JSON.parse(JSON.stringify(route))
  });
}

function buildRouteFallbackSvg(route) {
  const points = Array.isArray(route?.points) ? route.points : [];
  if (!points.length) {
    return '<div class="route-map-empty">完成一次户外运动后，这里会展示你的运动轨迹。</div>';
  }

  const polyline = points.map(([x, y]) => `${x * 3.2},${y * 2.28}`).join(" ");
  const checkpoints = Array.isArray(route?.checkpoints) ? route.checkpoints : [];
  const startPoint = points[0];
  const endPoint = points[points.length - 1];

  return `
    <svg class="route-map-svg" viewBox="0 0 320 228" role="img" aria-label="户外运动轨迹">
      <defs>
        <linearGradient id="route-bg" x1="0" x2="1" y1="0" y2="1">
          <stop offset="0%" stop-color="#eef6ea"/>
          <stop offset="100%" stop-color="#e6edf8"/>
        </linearGradient>
        <linearGradient id="route-line" x1="0" x2="1" y1="0" y2="0">
          <stop offset="0%" stop-color="#ffe100"/>
          <stop offset="100%" stop-color="#ffd148"/>
        </linearGradient>
      </defs>
      <rect x="0" y="0" width="320" height="228" rx="24" fill="url(#route-bg)"/>
      <g opacity="0.26" stroke="#c3d5bf" stroke-width="1">
        <path d="M18 40 H302"/>
        <path d="M18 88 H302"/>
        <path d="M18 136 H302"/>
        <path d="M18 184 H302"/>
        <path d="M64 20 V208"/>
        <path d="M128 20 V208"/>
        <path d="M192 20 V208"/>
        <path d="M256 20 V208"/>
      </g>
      <polyline points="${polyline}" fill="none" stroke="#19222b" stroke-width="9" stroke-linecap="round" stroke-linejoin="round" opacity="0.18"/>
      <polyline points="${polyline}" fill="none" stroke="url(#route-line)" stroke-width="5.5" stroke-linecap="round" stroke-linejoin="round"/>
      ${checkpoints
        .map(
          (item) => `
            <g transform="translate(${item.x * 3.2}, ${item.y * 2.28})">
              <circle r="10" fill="#121212"/>
              <text y="3" text-anchor="middle" font-size="10" font-weight="700" fill="#ffffff">${escapeHtml(item.label)}</text>
            </g>
          `
        )
        .join("")}
      <g transform="translate(${startPoint[0] * 3.2}, ${startPoint[1] * 2.28})">
        <circle r="7" fill="#1fd27b" stroke="#ffffff" stroke-width="2"/>
      </g>
      <g transform="translate(${endPoint[0] * 3.2}, ${endPoint[1] * 2.28})">
        <circle r="7" fill="#ff6b58" stroke="#ffffff" stroke-width="2"/>
      </g>
    </svg>
  `;
}

function renderRouteMap(route, mapId = "") {
  if (canRenderAmapRoute(route) && mapId) {
    registerRouteMap(route, mapId);
    return `<div class="route-map-live" data-route-map="${escapeHtml(mapId)}" aria-label="户外运动轨迹地图"></div>`;
  }

  return buildRouteFallbackSvg(route);
}

function loadAmapSdk() {
  const config = getAmapRuntimeConfig();
  if (!config) {
    return Promise.reject(new Error("未配置高德地图 Key。"));
  }

  if (window.AMap?.Map) {
    return Promise.resolve(window.AMap);
  }

  if (mapSdkPromise && mapSdkProvider === "amap") {
    return mapSdkPromise;
  }

  mapSdkProvider = "amap";
  mapSdkPromise = new Promise((resolve, reject) => {
    if (config.amapSecurityCode) {
      window._AMapSecurityConfig = {
        ...(window._AMapSecurityConfig || {}),
        securityJsCode: config.amapSecurityCode
      };
    }

    const existing = document.getElementById("fithub-amap-sdk");
    if (existing) {
      existing.addEventListener("load", () => resolve(window.AMap), { once: true });
      existing.addEventListener("error", () => reject(new Error("高德地图 SDK 加载失败")), { once: true });
      return;
    }

    const script = document.createElement("script");
    script.id = "fithub-amap-sdk";
    script.async = true;
    script.src = `https://webapi.amap.com/maps?v=2.0&key=${encodeURIComponent(config.amapKey)}`;
    script.onload = () => {
      if (window.AMap?.Map) {
        resolve(window.AMap);
      } else {
        reject(new Error("高德地图 SDK 未初始化成功。"));
      }
    };
    script.onerror = () => reject(new Error("高德地图 SDK 加载失败"));
    document.head.appendChild(script);
  }).catch((error) => {
    mapSdkPromise = null;
    throw error;
  });

  return mapSdkPromise;
}

function initAmapRouteMap(container, AMap, route) {
  if (!container || container.dataset.routeMapHydrated === "1") return;
  const geoPoints = Array.isArray(route?.geoPoints)
    ? route.geoPoints
        .map((item) => wgs84ToGcj02(Number(item.lng), Number(item.lat)))
        .filter(([lng, lat]) => Number.isFinite(lng) && Number.isFinite(lat))
    : [];

  if (!geoPoints.length) {
    container.innerHTML = buildRouteFallbackSvg(route);
    container.dataset.routeMapHydrated = "1";
    return;
  }

  const map = new AMap.Map(container, {
    viewMode: "2D",
    zoom: 14,
    center: geoPoints[0],
    mapStyle: "amap://styles/whitesmoke",
    resizeEnable: true,
    dragEnable: true,
    zoomEnable: true,
    jogEnable: false
  });

  const overlays = [];

  if (geoPoints.length >= 2) {
    overlays.push(
      new AMap.Polyline({
        path: geoPoints,
        strokeColor: "#ffe066",
        strokeWeight: 6,
        strokeOpacity: 0.96,
        lineJoin: "round",
        lineCap: "round"
      })
    );
  }

  const startMarker = new AMap.CircleMarker({
    center: geoPoints[0],
    radius: 7,
    strokeColor: "#ffffff",
    strokeWeight: 3,
    fillColor: "#1fd27b",
    fillOpacity: 1
  });

  overlays.push(startMarker);

  if (geoPoints.length >= 2) {
    overlays.push(
      new AMap.CircleMarker({
        center: geoPoints[geoPoints.length - 1],
        radius: 7,
        strokeColor: "#ffffff",
        strokeWeight: 3,
        fillColor: "#ff6b58",
        fillOpacity: 1
      })
    );
  }

  map.add(overlays);
  if (geoPoints.length >= 2) {
    map.setFitView(overlays, false, [28, 28, 28, 28]);
  } else {
    map.setZoomAndCenter(16, geoPoints[0]);
  }
  container.dataset.routeMapHydrated = "1";
  container._fithubAmap = map;
}

async function hydrateRouteMaps(root = document) {
  const containers = Array.from(root.querySelectorAll("[data-route-map]"));
  if (!containers.length) return;
  if (!getAmapRuntimeConfig()) return;

  const AMap = await loadAmapSdk();
  containers.forEach((container) => {
    if (container.dataset.routeMapHydrated === "1") return;
    const payload = routeMapRegistry.get(container.dataset.routeMap);
    if (!payload?.route) return;
    try {
      initAmapRouteMap(container, AMap, payload.route);
    } catch (_error) {
      container.innerHTML = '<div class="route-map-empty">高德地图加载失败，已回退为普通轨迹图。</div>';
      container.dataset.routeMapHydrated = "1";
    }
  });
}

function renderOutdoorRouteFeature(profile) {
  const checkin = getOutdoorShareCheckin(profile);
  if (!checkin?.route) {
    return '<article class="empty-card">完成一次户外跑步、行走、骑行或徒步后，这里会自动生成轨迹分享页。</article>';
  }

  const route = checkin.route;
  const speedOrPaceLabel = checkin.sportId === "outdoor-cycling" ? "平均速度" : "平均配速";
  const speedOrPaceValue =
    checkin.sportId === "outdoor-cycling"
      ? `${Math.max(8, Math.round((route.distanceKm / Math.max(1, checkin.duration / 60)) * 10) / 10)} km/h`
      : `${route.avgPaceLabel}/km`;

  return `
    <article class="route-share-card">
      <article class="route-share-map-shell route-share-map-shell--action" data-open-route-map-detail="${checkin.id}">
        <div class="route-share-map-head">
          <div>
            <strong>${escapeHtml(route.shareTitle || `${route.city || "厦门"} ${checkin.sportLabel}`)}</strong>
            <p>${escapeHtml(route.dateLabel || formatShareDateLabel(checkin.createdAt))}</p>
          </div>
          <span class="status-pill">${escapeHtml(route.district || profile.locationLabel || state.userPosition.label)}</span>
        </div>
        <div class="route-share-map-canvas">
          ${renderRouteMap(route, checkin.id)}
          <span class="route-share-map-hint">点开地图，查看更完整的轨迹详情</span>
        </div>
      </article>

      <article class="route-share-stat-board">
        <div class="route-share-topline">
          <div>
            <span>距离</span>
            <strong>${escapeHtml(`${route.distanceKm || checkin.distance || 0} km`)}</strong>
          </div>
          <div>
            <span>运动类型</span>
            <strong>${escapeHtml(checkin.sportLabel || "户外运动")}</strong>
          </div>
        </div>

        <div class="route-share-grid">
          <div><span>运动时间</span><strong>${escapeHtml(route.durationLabel || formatWorkoutDurationLabel((checkin.duration || 0) * 60))}</strong></div>
          <div><span>${escapeHtml(speedOrPaceLabel)}</span><strong>${escapeHtml(speedOrPaceValue)}</strong></div>
          <div><span>最快 1 公里</span><strong>${escapeHtml(route.bestPaceLabel ? `${route.bestPaceLabel}/km` : "--")}</strong></div>
          <div><span>平均心率</span><strong>${escapeHtml(route.avgHeartRate ? `${route.avgHeartRate} bpm` : "--")}</strong></div>
          <div><span>累计上升</span><strong>${escapeHtml(route.elevationGain ? `${route.elevationGain} m` : "--")}</strong></div>
          <div><span>卡路里</span><strong>${escapeHtml(`${route.calories || checkin.calories || 0} kcal`)}</strong></div>
        </div>

        <p class="result-tip">${
          escapeHtml(
            canRenderAmapRoute(route)
              ? "这次轨迹已按真实 GPS 点位叠加高德地图底图生成。"
              : Array.isArray(route.geoPoints) && route.geoPoints.length
                ? "这次轨迹已按真实 GPS 点位生成；当前点位过少或地图服务暂未就绪时，会先显示简化轨迹图。"
                : "这是一张适合分享的户外运动成绩页；如果允许定位，后面会优先按真实 GPS 点位生成轨迹。"
          )
        }</p>

        <div class="action-row action-row--checkin">
          <button class="primary-submit" data-back-profile="1" type="button">返回</button>
        </div>
      </article>
    </article>
  `;
}

function renderOutdoorRouteMapDetail(profile) {
  const checkin = getOutdoorShareCheckin(profile);
  if (!checkin?.route) {
    return '<article class="empty-card">完成一次户外运动后，这里会展示更完整的轨迹地图详情。</article>';
  }

  const route = checkin.route;
  const pointCount = Array.isArray(route.geoPoints) ? route.geoPoints.length : 0;
  const mapId = `${checkin.id}-detail`;

  return `
    <article class="route-detail-card">
      <div class="route-share-map-shell route-share-map-shell--detail">
        <div class="route-share-map-head">
          <div>
            <strong>${escapeHtml(route.shareTitle || `${route.city || "厦门"} ${checkin.sportLabel}`)}</strong>
            <p>${escapeHtml(route.dateLabel || formatShareDateLabel(checkin.createdAt))}</p>
          </div>
          <span class="status-pill">${escapeHtml(checkin.sportLabel || "户外运动")}</span>
        </div>
        <div class="route-share-map-canvas route-share-map-canvas--detail">
          ${renderRouteMap(route, mapId)}
        </div>
      </div>

      <article class="route-share-stat-board route-share-stat-board--detail">
        <div class="route-share-topline">
          <div>
            <span>距离</span>
            <strong>${escapeHtml(`${route.distanceKm || checkin.distance || 0} km`)}</strong>
          </div>
          <div>
            <span>定位点</span>
            <strong>${escapeHtml(`${pointCount} 个`)}</strong>
          </div>
        </div>

        <div class="route-share-grid">
          <div><span>运动时间</span><strong>${escapeHtml(route.durationLabel || formatWorkoutDurationLabel((checkin.duration || 0) * 60))}</strong></div>
          <div><span>平均配速</span><strong>${escapeHtml(route.avgPaceLabel ? `${route.avgPaceLabel}/km` : "--")}</strong></div>
          <div><span>最快 1 公里</span><strong>${escapeHtml(route.bestPaceLabel ? `${route.bestPaceLabel}/km` : "--")}</strong></div>
          <div><span>平均心率</span><strong>${escapeHtml(route.avgHeartRate ? `${route.avgHeartRate} bpm` : "--")}</strong></div>
          <div><span>累计上升</span><strong>${escapeHtml(route.elevationGain ? `${route.elevationGain} m` : "--")}</strong></div>
          <div><span>卡路里</span><strong>${escapeHtml(`${route.calories || checkin.calories || 0} kcal`)}</strong></div>
        </div>

        <p class="result-tip">${escapeHtml(pointCount > 1 ? "这张地图正在直接使用你本次运动采集到的真实定位点。" : "当前只采集到 1 个真实定位点，所以地图会先落在真实位置点上；下次多移动一小段，轨迹线会更完整。")}</p>

        <div class="action-row action-row--checkin">
          <button class="primary-submit" data-back-profile="1" type="button">返回</button>
        </div>
      </article>
    </article>
  `;
}

function renderFavoriteSportEditor(profile) {
  const selectedIds = state.checkinSelectionDraft.length
    ? state.checkinSelectionDraft
    : [...(profile.favoriteSports || [])];
  const canSave = selectedIds.length > 0;
  const sections = getSportPickerSections(selectedIds);

  return `
    <article class="detail-card checkin-feature-card sport-picker-sheet">
      <div class="sport-picker-handle"></div>
      <div class="section-title-row section-title-row--sport-picker">
        <div>
          <h3>选择日常运动</h3>
          <p class="result-tip">保留你最常用的项目，后面打开就能直接 GO。</p>
        </div>
        <span class="status-pill">${selectedIds.length} 项</span>
      </div>

      <section class="sport-picker-section-stack">
        ${sections
          .map(
            (section) => `
              <article class="sport-picker-section">
                <span class="sport-picker-label">${escapeHtml(section.label)}</span>
                <div class="checkin-sport-grid">
                  ${section.sports
                    .map(
                      (item) => `
                        <button
                          class="checkin-sport-button ${selectedIds.includes(item.id) ? "is-active" : ""}"
                          data-toggle-common-sport="${item.id}"
                          type="button"
                        >
                          <span class="checkin-sport-icon">${escapeHtml(item.icon)}</span>
                          <strong>${escapeHtml(item.label)}</strong>
                          <small>${escapeHtml(item.hint)}</small>
                        </button>
                      `
                    )
                    .join("")}
                </div>
              </article>
            `
          )
          .join("")}
      </section>

      <div class="action-row action-row--checkin">
        <button class="mini-button" data-cancel-common-sports="1" type="button">取消</button>
        <button class="primary-submit" ${canSave ? "" : "disabled"} data-save-common-sports="1" type="button">完成选择</button>
      </div>
    </article>
  `;
}

function renderWorkoutLauncher(profile) {
  const favoriteSports = getFavoriteSports(profile);
  const currentSport = getCurrentWorkoutSport(profile);
  const connectedDevices = getConnectedDevices(profile);
  const bodySummary = `${profile.gender || "未填"} · ${getProfileWeight(profile) || "--"} kg`;
  const deviceSummary = connectedDevices.length ? `已连接 ${connectedDevices.length} 台设备` : "未连接设备";
  const finishState = state.workoutFinishing;
  const isSavingWorkout = finishState?.status === "saving";
  const saveStatusMarkup = finishState
    ? `
        <article class="helper-card helper-card--workout-sync">
          <strong>${escapeHtml(isSavingWorkout ? "正在保存打卡" : "打卡保存失败")}</strong>
          <p>${escapeHtml(finishState.message || (isSavingWorkout ? "本次训练已先退出运动模式，系统正在后台补定位并保存。" : "本次训练仍保留在本机，你可以重新尝试保存。"))}</p>
          ${
            isSavingWorkout
              ? `<span class="status-pill">请稍等 1-2 秒</span>`
              : `<div class="action-row action-row--checkin"><button class="primary-submit" data-retry-finish-workout="1" type="button">重新保存这次训练</button></div>`
          }
        </article>
      `
    : "";

  if (!favoriteSports.length || state.checkinEditing) {
    return renderFavoriteSportEditor(profile);
  }

  return `
    <article class="detail-card checkin-feature-card workout-studio-card">
      ${saveStatusMarkup}
      <div class="section-title-row workout-studio-head">
        <div>
          <span class="dashboard-checkin-kicker">今日运动</span>
          <h3>选一个常用项目，直接开始</h3>
        </div>
        <button class="mini-button" ${isSavingWorkout ? "disabled" : ""} data-edit-common-sports="1" type="button">切换项目</button>
      </div>

      <div class="dashboard-checkin-pills dashboard-checkin-pills--toolbar workout-type-strip">
        ${favoriteSports
          .map(
            (item) => `
              <button
                class="workout-type-chip ${item.id === currentSport.id ? "is-active" : ""}"
                data-select-workout-sport="${item.id}"
                ${isSavingWorkout ? "disabled" : ""}
                type="button"
              >
                ${escapeHtml(item.label)}
              </button>
            `
          )
          .join("")}
      </div>

      ${
        state.workoutSession
          ? renderWorkoutSession(profile)
          : `
            <article class="workout-start-panel">
              <div class="workout-start-copy">
                <span class="workout-start-kicker">准备开始</span>
                <h2>${escapeHtml(currentSport ? currentSport.label : "先选择运动")}</h2>
                <p>${escapeHtml(currentSport ? currentSport.hint : "先在上方选一个日常运动项目。")}</p>
              </div>

              <div class="workout-start-meta">
                <span>${escapeHtml(bodySummary)}</span>
                <span>${escapeHtml(deviceSummary)}</span>
              </div>

              <button class="workout-go-orb" ${isSavingWorkout ? "disabled" : ""} ${currentSport ? 'data-go-workout="1"' : 'data-edit-common-sports="1"'} type="button">
                <small>运动</small>
                <strong>${isSavingWorkout ? "保存中" : currentSport ? "GO" : "选项目"}</strong>
              </button>

              <div class="workout-start-footer">
                <button class="text-link" data-open-my-feature="health" type="button">${connectedDevices.length ? "管理设备" : "连接设备"}</button>
                <span>${escapeHtml(isSavingWorkout ? "正在后台补最后一个定位点并同步这次训练。" : currentSport ? "按下 GO 后会直接进入全屏运动记录。" : "第一次先选项目，避免默认进跑步。")}</span>
              </div>
            </article>
          `
      }
    </article>
  `;
}

function renderWorkoutSession(profile) {
  const session = getWorkoutSessionStats(profile);
  if (!session) return "";
  const gpsStatus = supportsOutdoorRouteShare(session.sport.id) ? getOutdoorGpsStatus(session) : "";
  const isPaused = Boolean(state.workoutSession?.pausedAt);
  const estimatedHeartRate = profile.restingHeartRate
    ? `${Math.round(Number(profile.restingHeartRate) + (supportsOutdoorRouteShare(session.sport.id) ? 62 : 48))} bpm`
    : "--";
  const metricLabel = supportsOutdoorRouteShare(session.sport.id) ? "距离" : "时长";
  const metricValue = supportsOutdoorRouteShare(session.sport.id)
    ? (session.distance ? `${session.distance} km` : "0.00 km")
    : `${session.elapsedMinutes} 分钟`;
  const paceLabel = supportsOutdoorRouteShare(session.sport.id)
    ? formatWorkoutPaceLabel(session.elapsedMinutes, session.distance)
    : getProfileBMI(profile);
  const paceTitle = supportsOutdoorRouteShare(session.sport.id) ? "平均配速" : "BMI";

  return `
    <section class="workout-live-screen">
      <div class="workout-live-screen-top">
        <div class="workout-live-picker workout-live-picker--static">${escapeHtml(session.sport.label)}</div>
        <span class="workout-live-chip workout-live-chip--muted">${escapeHtml(gpsStatus || session.sourceLabel)}</span>
      </div>

      <article class="detail-card workout-session-card workout-session-card--live">
        <div class="workout-live-top">
          <span class="workout-live-chip">${escapeHtml(isPaused ? "已暂停" : "正在记录")}</span>
          <span class="workout-live-chip workout-live-chip--accent">${escapeHtml(session.sport.hint || "运动记录中")}</span>
        </div>

        <div class="workout-live-value">
          <strong>${escapeHtml(String(session.calories))}</strong>
          <span>总卡路里 / kcal</span>
        </div>

        <div class="workout-live-stat-grid">
          <div>
            <span>持续时间</span>
            <strong>${escapeHtml(session.timerLabel)}</strong>
          </div>
          <div>
            <span>${escapeHtml(metricLabel)}</span>
            <strong>${escapeHtml(metricValue)}</strong>
          </div>
          <div>
            <span>估算心率</span>
            <strong>${escapeHtml(estimatedHeartRate)}</strong>
          </div>
          <div>
            <span>${escapeHtml(paceTitle)}</span>
            <strong>${escapeHtml(paceLabel || "--")}</strong>
          </div>
        </div>

        <div class="workout-live-actions">
          <button class="workout-live-side" data-cancel-workout="1" type="button">放弃</button>
          <button class="workout-live-finish" data-finish-workout="1" type="button">结束打卡</button>
          <button class="workout-live-side workout-live-side--pause ${isPaused ? "is-active" : ""}" data-pause-workout="1" type="button">${isPaused ? "继续" : "暂停"}</button>
        </div>
      </article>
    </section>
  `;
}

function renderCheckinFeature(profile) {
  const needsHealthData = !profile.gender || !getProfileHeight(profile) || !getProfileWeight(profile);

  return `
    ${
      needsHealthData
        ? `
          <article class="detail-card">
            <div class="section-title-row">
              <div>
                <h3>先补全健康数据</h3>
                <p class="result-tip">打卡的卡路里估算会用到性别、身高和体重，建议先到“健康”里完善。</p>
              </div>
              <button class="mini-button mini-button--accent" data-open-my-feature="health" type="button">去健康</button>
            </div>
          </article>
        `
        : ""
    }
    ${renderWorkoutLauncher(profile)}
    <article class="detail-card">
      <div class="section-title-row">
        <div>
          <h3>最近打卡</h3>
          <p class="result-tip">结束训练后会自动沉淀到这里，并同步进入你的“我的动态”。</p>
        </div>
      </div>
      ${renderCheckinHistory(profile)}
    </article>
  `;
}

function renderHealthFeature(profile) {
  const dashboard = buildHealthDashboard(profile);
  const connectedSet = new Set(getConnectedDevices(profile));
  const latestSource = profile.healthSource || "等待同步";
  const latestSync = profile.deviceSyncedAt || "尚未同步";
  const showOverview = state.healthViewMode === "overview" || state.healthViewMode === "all";
  const showTrends = state.healthViewMode === "trends" || state.healthViewMode === "all";

  const renderSportCard = (card) => `
    <article
      class="health-sport-card"
      style="--health-accent:${card.accent}; --health-soft:${card.soft};"
    >
      <div class="health-card-head">
        <div class="health-card-title">
          <span class="health-icon">${escapeHtml(card.icon)}</span>
          <div>
            <strong>${escapeHtml(card.label)}</strong>
            <p>${escapeHtml(card.compareLabel)}</p>
          </div>
        </div>
        <span class="health-card-value">${escapeHtml(card.totalLabel)}</span>
      </div>
      ${renderHealthSparkline(card.series, {
        emptyLabel: `本月暂无${card.label}记录`
      })}
      ${
        card.id === "run"
          ? `
            <div class="health-card-subcopy">
              最近 ${dashboard.runPaceRows.length || 0} 次跑步，${dashboard.runPaceRows.length ? `最快配速 ${escapeHtml(formatPaceSeconds(Math.min(...dashboard.runPaceRows.map((item) => item.seconds))))}` : "暂时还没有配速记录"}
            </div>
            ${renderRunPaceRows(dashboard.runPaceRows)}
          `
          : `
            <div class="health-card-subcopy">
              ${card.id === "yoga" ? "按近 12 周统计时长变化" : "按本月累计趋势显示"}，数据来自你的真实训练记录。
            </div>
          `
      }
    </article>
  `;

  return `
    <section class="health-center">
      <article class="health-report-banner">
        <div>
          <span class="health-report-chip">${escapeHtml(dashboard.weekLabel)}</span>
          <strong>本周已累计运动 ${escapeHtml(formatHealthMinutes(dashboard.sevenDayTotal))}</strong>
          <p>把你的训练、步数、身体数据和设备同步统一沉淀成一页数据中心。</p>
        </div>
        <button class="mini-button mini-button--accent" data-set-health-view="all" type="button">去查看</button>
      </article>

      ${renderHealthViewTabs()}

      ${
        showOverview
          ? `
            <article class="health-overview-card">
              <div class="health-overview-copy">
                <span class="health-section-kicker">总运动</span>
                <h3>本月累计运动 ${dashboard.monthActiveDays} 天，最近连续运动 ${dashboard.streakDays} 天</h3>
                <p>${escapeHtml(dashboard.comparisonLabel)}</p>
              </div>
              <div class="health-overview-stats">
                <div><span>运动时长</span><strong>${escapeHtml(formatHealthMinutes(dashboard.monthMinutes))}</strong></div>
                <div><span>卡路里</span><strong>${escapeHtml(formatHealthNumber(dashboard.monthCalories, 0))} kcal</strong></div>
                <div><span>总距离</span><strong>${escapeHtml(formatHealthDistance(dashboard.monthDistance))} km</strong></div>
                <div><span>已连设备</span><strong>${connectedSet.size ? escapeHtml(`${connectedSet.size} 台`) : "未连接"}</strong></div>
              </div>
              ${renderHealthCalendar(dashboard.calendar)}
              <div class="health-today-compare">
                <div>
                  <span>今日</span>
                  <strong>${escapeHtml(formatHealthMinutes(dashboard.todayMinutes))}</strong>
                </div>
                <div>
                  <span>昨天</span>
                  <strong>${escapeHtml(formatHealthMinutes(dashboard.yesterdayMinutes))}</strong>
                </div>
              </div>
            </article>

            <section class="health-summary-grid">
              <article class="health-summary-card summary-card--health">
                <div class="health-card-head health-card-head--compact">
                  <div class="health-card-title">
                    <span class="health-icon">体</span>
                    <div>
                      <strong>身体数据</strong>
                      <p>体型与恢复状态会直接影响训练估算</p>
                    </div>
                  </div>
                  <span class="health-inline-note">来源：${escapeHtml(latestSource)}</span>
                </div>
                <div class="health-metrics-grid">
                  ${dashboard.bodyMetrics
                    .map(
                      (item) => `
                        <div class="health-metric-cell">
                          <span>${escapeHtml(item.label)}</span>
                          <strong>${escapeHtml(item.value)}</strong>
                          <small>${escapeHtml(item.note)}</small>
                        </div>
                      `
                    )
                    .join("")}
                </div>
              </article>

              <article class="health-summary-card">
                <div class="health-card-head health-card-head--compact">
                  <div class="health-card-title">
                    <span class="health-icon">步</span>
                    <div>
                      <strong>步数</strong>
                      <p>${dashboard.steps.source ? `${escapeHtml(dashboard.steps.source)} 已同步` : "连接设备后可同步真实步数"}</p>
                    </div>
                  </div>
                  <span class="health-inline-note">${escapeHtml(dashboard.steps.syncedAt || "未同步")}</span>
                </div>
                <div class="health-step-highlight">
                  <div>
                    <span>今日</span>
                    <strong>${dashboard.steps.today ? `${escapeHtml(formatHealthNumber(dashboard.steps.today, 0))} 步` : "--"}</strong>
                  </div>
                  <div>
                    <span>昨天</span>
                    <strong>${dashboard.steps.yesterday ? `${escapeHtml(formatHealthNumber(dashboard.steps.yesterday, 0))} 步` : "--"}</strong>
                  </div>
                  <div>
                    <span>7 日均值</span>
                    <strong>${dashboard.steps.average ? `${escapeHtml(formatHealthNumber(dashboard.steps.average, 0))} 步` : "--"}</strong>
                  </div>
                </div>
                ${renderHealthBarChart(dashboard.steps.series, {
                  formatter: (value) => (value ? formatHealthNumber(value, 0) : ""),
                  emptyLabel: "最近 7 天步数会在连接设备后自动累计"
                })}
              </article>

              <article class="health-summary-card">
                <div class="health-card-head health-card-head--compact">
                  <div class="health-card-title">
                    <span class="health-icon">氧</span>
                    <div>
                      <strong>最大摄氧量</strong>
                      <p>${dashboard.vo2.source ? `${escapeHtml(dashboard.vo2.source)} 同步中` : "等待设备同步 cardio fitness"}</p>
                    </div>
                  </div>
                  <span class="health-inline-note">最近消耗 ${escapeHtml(dashboard.vo2.activeEnergy)}</span>
                </div>
                <div class="health-vo2-value">
                  <strong>${escapeHtml(dashboard.vo2.value)}</strong>
                  <span>${dashboard.vo2.value !== "--" ? "ml/kg/min" : "暂无设备数据"}</span>
                </div>
                <p class="result-tip result-tip--health">
                  连接 Apple Health、Apple Watch 或小米设备后，这里会自动沉淀更完整的心肺耐力数据。
                </p>
              </article>
            </section>

            <article class="health-device-card">
              <div class="health-card-head">
                <div class="health-card-title">
                  <span class="health-icon">设</span>
                  <div>
                    <strong>设备与来源</strong>
                    <p>同步后会自动更新步数、体脂、心率和近期训练趋势</p>
                  </div>
                </div>
                <span class="health-inline-note">${escapeHtml(latestSync)}</span>
              </div>
              <section class="device-list">
                <article class="device-row">
                  <div>
                    <strong>Apple Watch</strong>
                    <p>同步运动时长、卡路里、心率与训练状态</p>
                  </div>
                  ${
                    connectedSet.has("Apple Watch")
                      ? '<span class="status-pill">已连接</span>'
                      : '<button class="mini-button mini-button--accent" data-sync-health-device="apple-watch" type="button">连接设备</button>'
                  }
                </article>
                <article class="device-row">
                  <div>
                    <strong>小米手表</strong>
                    <p>同步日常活动、训练记录和基础身体数据</p>
                  </div>
                  ${
                    connectedSet.has("小米手表")
                      ? '<span class="status-pill">已连接</span>'
                      : '<button class="mini-button mini-button--accent" data-sync-health-device="xiaomi-watch" type="button">连接设备</button>'
                  }
                </article>
                <article class="device-row">
                  <div>
                    <strong>小米智能秤</strong>
                    <p>同步体重、BMI、体脂率与最近一次测量时间</p>
                  </div>
                  ${
                    connectedSet.has("小米智能秤")
                      ? '<span class="status-pill">已连接</span>'
                      : '<button class="mini-button mini-button--accent" data-sync-health-device="xiaomi-scale" type="button">连接设备</button>'
                  }
                </article>
              </section>
            </article>
          `
          : ""
      }

      ${
        showTrends
          ? `
            <article class="health-trend-card">
              <div class="health-card-head">
                <div class="health-card-title">
                  <span class="health-icon">势</span>
                  <div>
                    <strong>总运动趋势</strong>
                    <p>过去 7 天平均运动 ${escapeHtml(formatHealthMinutes(dashboard.sevenDayAverage))}</p>
                  </div>
                </div>
                <span class="health-inline-note">${escapeHtml(dashboard.weekLabel)}</span>
              </div>
              ${renderHealthBarChart(dashboard.sevenDaySeries, {
                formatter: (value) => (value ? formatHealthNumber(value, 0) : ""),
                emptyLabel: "最近 7 天还没有训练数据"
              })}
            </article>

            <section class="health-trend-grid">
              ${dashboard.sportCards.map(renderSportCard).join("")}
            </section>
          `
          : ""
      }
    </section>
  `;
}

function renderPersonalDashboardPage(profile, managedProfiles) {
  const stats = getManagedDashboardStats(profile);
  const relatedBookings = getRelevantBookingsForProfile(profile);
  const shortcutTiles =
    profile.role === "enthusiast"
      ? [
          renderPersonalShortcutTile("账户", "资料与安全", "账", 'data-open-my-feature="account"'),
          renderPersonalShortcutTile("商城", "器材与精选商品", "商", 'data-open-my-feature="shop"'),
          renderPersonalShortcutTile("消息", `${getInboxCount()} 条互动`, "信", 'data-open-my-feature="messages"'),
          renderPersonalShortcutTile("订单", "预约记录", "单", 'data-open-my-feature="orders"'),
          renderPersonalShortcutTile("关注", "我关注的", "关", 'data-open-my-feature="favorites"'),
          renderPersonalShortcutTile("收藏", `${getFavoritedMediaEntries().length} 条媒体`, "藏", 'data-open-my-feature="collections"'),
          renderPersonalShortcutTile("积分", `${getProfilePoints(profile, relatedBookings)} 分`, "分", 'data-open-my-feature="points"'),
          renderPersonalShortcutTile("健康", "数据中心", "健", 'data-open-my-feature="health"')
        ]
      : [
          renderPersonalShortcutTile("账户", "资料与主页", "账", 'data-open-my-feature="account"'),
          renderPersonalShortcutTile("商城", "器材、周边与门店商品", "商", 'data-open-my-feature="shop"'),
          renderPersonalShortcutTile("消息", `${getInboxCount()} 条互动`, "信", 'data-open-my-feature="messages"'),
          renderPersonalShortcutTile("订单", `别人给我的 ${relatedBookings.length} 单`, "单", 'data-open-my-feature="orders"'),
          renderPersonalShortcutTile("关注", "我关注的", "关", 'data-open-my-feature="favorites"'),
          renderPersonalShortcutTile("收藏", `${getFavoritedMediaEntries().length} 条媒体`, "藏", 'data-open-my-feature="collections"'),
          renderPersonalShortcutTile("评分", profile.ratingCount ? `${getRatingDisplay(profile)} 分` : "等待评分", "评", 'data-open-my-feature="reviews"'),
          renderPersonalShortcutTile("健康", "数据中心", "健", 'data-open-my-feature="health"')
        ];
  const roleSummary =
    profile.role === "enthusiast"
      ? renderCheckinEntry(profile)
      : `
          <article class="dashboard-summary dashboard-summary--managed">
            <div class="section-title-row">
              <div>
                <h3>${profile.role === "coach" ? "最近收到的预约" : "最近收到的订单"}</h3>
                <p class="result-tip">${profile.role === "coach" ? "用户预约你的私教课程后，会优先出现在这里。" : "用户预约你的场馆后，会优先出现在这里。"}</p>
              </div>
              <button class="mini-button mini-button--accent" data-open-my-feature="schedule" type="button">查看全部</button>
            </div>
            ${renderManagedBookingList(profile, relatedBookings.slice(0, 2), {
              emptyText: profile.role === "coach" ? "暂时还没有人预约你，完善主页和价格后，这里会出现新的预约消息。" : "暂时还没有人预约你的场馆，完善主页和价格后，这里会出现新的到店订单。",
              primaryAction: "查看预约"
            })}
          </article>
        `;

  return `
    <section class="managed-strip managed-strip--dashboard">
      ${managedProfiles
        .map(
          (item) => `
            <button class="managed-chip ${item.id === profile.id ? "is-active" : ""}" data-switch-managed="${item.id}" type="button">
              ${escapeHtml(getRoleLabel(item.role))}
            </button>
          `
        )
        .join("")}
    </section>

    <article class="dashboard-card">
      <div class="dashboard-profile-row">
        <div class="dashboard-profile-main">
          ${renderAvatarMarkup(profile, "avatar avatar--large")}
          <div>
            <h2>${escapeHtml(profile.name)}</h2>
            <p>${escapeHtml(profile.handle)}</p>
            <span>${escapeHtml(profile.locationLabel)}</span>
          </div>
        </div>
        <button class="mini-button" data-edit-role="${profile.role}" type="button">编辑资料</button>
      </div>

      <div class="dashboard-stats">
        ${stats
          .map(
            (item) => `
              <div>
                <strong>${escapeHtml(item.value)}</strong>
                <span>${escapeHtml(item.label)}</span>
              </div>
            `
          )
          .join("")}
      </div>

      ${roleSummary}
    </article>

    <section class="account-section">
      <div class="section-title-row">
        <h3>我的功能</h3>
        <button class="text-link" data-open-role-picker="1" type="button">切换身份</button>
      </div>
      <div class="account-grid">
        ${shortcutTiles.join("")}
      </div>
    </section>

    <section class="section-title-row section-title-row--moments">
      <div>
        <h3>我的动态</h3>
        <p class="result-tip">按发布时间从近到远展示，像微信朋友圈一样记录自己的训练生活。</p>
      </div>
      <button class="text-link" data-open-profile="${profile.id}" type="button">刷新</button>
    </section>

    ${renderPersonalMoments(profile)}
  `;
}

function renderFavoriteProfilesSection() {
  const followedProfiles = getFollowedProfiles();

  if (!followedProfiles.length) {
    return '<article class="empty-card">你还没有关注任何对象，先去探索页点几个感兴趣的人或场馆吧。</article>';
  }

  return `
    <section class="feature-follow-list">
      ${followedProfiles
        .map(
          (item) => `
            <article class="feature-follow-item">
              <button class="feature-follow-main" data-open-profile="${item.id}" type="button">
                ${renderAvatarMarkup(item, "avatar")}
                <div>
                  <strong>${escapeHtml(item.name)}</strong>
                  <p>${escapeHtml(getRoleLabel(item.role))} · ${escapeHtml(item.locationLabel || item.city || "未填写位置")}</p>
                </div>
              </button>
              <button class="follow-button is-active" data-toggle-follow="${item.id}" type="button">已关注</button>
            </article>
          `
        )
        .join("")}
    </section>
  `;
}

function extractPriceNumber(price = "") {
  const matched = String(price).match(/(\d+(?:\.\d+)?)/);
  return matched ? Number(matched[1]) : 0;
}

function buildGeneratedShelfItems(profile) {
  if (!profile || profile.role === "enthusiast") return [];

  if (profile.role === "coach") {
    return [
      {
        id: `shop-own-${profile.id}-band`,
        category: "strength",
        title: `${profile.name} 推荐弹力带套装`,
        subtitle: "用于热身、激活与纠正动作模式的基础装备",
        price: "¥139",
        originalPrice: "¥169",
        badge: "你的货架",
        sellerProfileId: profile.id,
        sellerType: profile.role,
        city: profile.locationLabel || profile.city || "厦门",
        rating: profile.ratingAvg ? getRatingDisplay(profile) : "新上架",
        sold: "待售",
        stock: "可售 24 套",
        tags: ["私教推荐", "动作激活", "新客常购"],
        image: createShopArtwork({
          sticker: "COACH",
          title: "弹力带套装",
          subtitle: "TRAINING KIT",
          bgA: "#fff0e6",
          bgB: "#efb586",
          accent: "#f28c28"
        })
      },
      {
        id: `shop-own-${profile.id}-recovery`,
        category: "recovery",
        title: `${profile.name} 训练恢复组合`,
        subtitle: "拉伸带、筋膜球与恢复滚轴打包售卖",
        price: "¥229",
        originalPrice: "¥269",
        badge: "你的货架",
        sellerProfileId: profile.id,
        sellerType: profile.role,
        city: profile.locationLabel || profile.city || "厦门",
        rating: profile.ratingAvg ? getRatingDisplay(profile) : "新上架",
        sold: "待售",
        stock: "可售 12 套",
        tags: ["恢复", "体态改善", "课后推荐"],
        image: createShopArtwork({
          sticker: "REC",
          title: "恢复组合",
          subtitle: "RECOVERY PACK",
          bgA: "#f8f1ff",
          bgB: "#c8b2f8",
          accent: "#9062ea"
        })
      }
    ];
  }

  return [
    {
      id: `shop-own-${profile.id}-bottle`,
      category: "merch",
      title: `${profile.name} 联名摇摇杯`,
      subtitle: "门店会员和团课学员都能顺手带走的基础周边",
      price: "¥69",
      originalPrice: "¥89",
      badge: "你的货架",
      sellerProfileId: profile.id,
      sellerType: profile.role,
      city: profile.locationLabel || profile.city || "厦门",
      rating: profile.ratingAvg ? getRatingDisplay(profile) : "新上架",
      sold: "待售",
      stock: "可售 36 件",
      tags: ["门店周边", "会员复购", "联名"],
      image: createShopArtwork({
        sticker: "GYM",
        title: "联名摇摇杯",
        subtitle: "STORE MERCH",
        bgA: "#fff3ea",
        bgB: "#f4b78d",
        accent: "#e2703a"
      })
    },
    {
      id: `shop-own-${profile.id}-roller`,
      category: "recovery",
      title: `${profile.name} 训练恢复滚轴`,
      subtitle: "门店热卖的训练后放松单品，也适合线上售卖",
      price: "¥119",
      originalPrice: "¥149",
      badge: "你的货架",
      sellerProfileId: profile.id,
      sellerType: profile.role,
      city: profile.locationLabel || profile.city || "厦门",
      rating: profile.ratingAvg ? getRatingDisplay(profile) : "新上架",
      sold: "待售",
      stock: "可售 20 件",
      tags: ["恢复", "高频复购", "门店同款"],
      image: createShopArtwork({
        sticker: "ROLL",
        title: "恢复滚轴",
        subtitle: "GYM RECOVERY",
        bgA: "#eff7ff",
        bgB: "#accdf5",
        accent: "#5b92d6"
      })
    }
  ];
}

function getShopCatalog(profile) {
  const ownShelf = getManagedProfiles().some((item) => item.id === profile.id)
    ? SHOP_PRODUCTS.filter((item) => item.sellerProfileId === profile.id)
    : [];
  const ownedProducts = ownShelf.length ? ownShelf : buildGeneratedShelfItems(profile);
  const marketplaceProducts = SHOP_PRODUCTS.filter((item) => item.sellerProfileId !== profile.id);
  return {
    ownedProducts,
    marketplaceProducts,
    allProducts: [...ownedProducts, ...marketplaceProducts]
  };
}

function getShopCategoryCount(items, categoryId) {
  if (categoryId === "all") return items.length;
  return items.filter((item) => item.category === categoryId).length;
}

function renderShopCategoryChips(items) {
  return `
    <div class="shop-category-row">
      ${SHOP_CATEGORY_OPTIONS.map((item) => {
        const isActive = (state.shopCategory || "all") === item.id;
        const count = getShopCategoryCount(items, item.id);
        return `
          <button
            class="shop-category-chip ${isActive ? "is-active" : ""}"
            data-shop-category="${item.id}"
            type="button"
          >
            <span>${escapeHtml(item.label)}</span>
            <small>${count}</small>
          </button>
        `;
      }).join("")}
    </div>
  `;
}

function getShopSellerMeta(product) {
  const sellerProfile = product.sellerProfileId ? getProfile(product.sellerProfileId) : null;
  if (sellerProfile) {
    return {
      profile: sellerProfile,
      name: sellerProfile.name,
      roleLabel: getRoleLabel(sellerProfile.role),
      location: sellerProfile.locationLabel || sellerProfile.city || product.city || "厦门"
    };
  }

  return {
    profile: {
      name: "FitHub 官方精选",
      avatar: "F"
    },
    name: "FitHub 官方精选",
    roleLabel: "平台自营",
    location: product.city || "厦门"
  };
}

function filterShopProducts(items) {
  if (!Array.isArray(items)) return [];
  if (!state.shopCategory || state.shopCategory === "all") return items;
  return items.filter((item) => item.category === state.shopCategory);
}

function renderShopProductCard(product, viewerProfile, { owned = false } = {}) {
  const seller = getShopSellerMeta(product);
  const isSelfOwned = Boolean(product.sellerProfileId && product.sellerProfileId === viewerProfile.id);
  const primaryAction = isSelfOwned
    ? `<button class="mini-button mini-button--accent" data-open-my-feature="orders" type="button">管理订单</button>`
    : product.sellerProfileId
      ? `<button class="mini-button mini-button--accent" data-open-chat="${product.sellerProfileId}" type="button">咨询购买</button>`
      : `<button class="mini-button mini-button--accent" data-open-my-feature="messages" type="button">联系平台</button>`;
  const secondaryAction = isSelfOwned
    ? `<button class="mini-button" data-open-profile="${viewerProfile.id}" type="button">查看主页</button>`
    : product.sellerProfileId
      ? `<button class="mini-button" data-open-profile="${product.sellerProfileId}" type="button">查看店铺</button>`
      : `<button class="mini-button" data-open-my-feature="orders" type="button">查看订单</button>`;

  return `
    <article class="shop-product-card ${owned ? "shop-product-card--owned" : ""}">
      <img class="shop-product-cover" src="${escapeHtml(product.image)}" alt="${escapeHtml(product.title)}" decoding="async">
      <div class="shop-product-body">
        <div class="shop-product-topline">
          <span class="status-pill">${escapeHtml(product.badge)}</span>
          <small>${escapeHtml(product.stock)}</small>
        </div>
        <h4>${escapeHtml(product.title)}</h4>
        <p>${escapeHtml(product.subtitle)}</p>
        <div class="shop-seller-row">
          <button class="shop-seller-button" ${product.sellerProfileId ? `data-open-profile="${product.sellerProfileId}"` : 'data-open-my-feature="messages"'} type="button">
            ${renderAvatarMarkup(seller.profile, "avatar shop-seller-avatar")}
            <div>
              <strong>${escapeHtml(seller.name)}</strong>
              <small>${escapeHtml(seller.roleLabel)} · ${escapeHtml(seller.location)}</small>
            </div>
          </button>
          <span class="shop-seller-score">★ ${escapeHtml(product.rating)}</span>
        </div>
        <div class="shop-tag-row">
          ${product.tags.map((tag) => `<span>${escapeHtml(tag)}</span>`).join("")}
        </div>
        <div class="shop-product-bottom">
          <div class="shop-price-block">
            <strong>${escapeHtml(product.price)}</strong>
            <small>${escapeHtml(product.originalPrice)}</small>
            <span>${escapeHtml(product.sold)}</span>
          </div>
          <div class="shop-product-actions">
            ${secondaryAction}
            ${primaryAction}
          </div>
        </div>
      </div>
    </article>
  `;
}

function renderShopFeature(profile) {
  const { ownedProducts, marketplaceProducts, allProducts } = getShopCatalog(profile);
  const filteredOwned = filterShopProducts(ownedProducts);
  const filteredMarketplace = filterShopProducts(marketplaceProducts);
  const sameCityCount = allProducts.filter((item) => String(item.city || "").includes(profile.city || state.userPosition.city)).length;
  const sellerCount = new Set(allProducts.map((item) => item.sellerProfileId || item.id)).size;
  const discountedCount = allProducts.filter((item) => extractPriceNumber(item.originalPrice) > extractPriceNumber(item.price)).length;
  const showOwnedSection = profile.role !== "enthusiast";
  const heroCopy =
    profile.role === "enthusiast"
      ? "把教练推荐器材、场馆同款装备和平台精选补给整合到一页，方便你从训练直接延伸到购买。"
      : profile.role === "coach"
        ? "你可以把教练推荐装备、恢复组合和训练周边放进货架，同时也能浏览平台热卖选品。"
        : "场馆可以把门店同款器材、周边和会员复购单品集中展示，方便用户直接从主页跳转咨询。";
  const summaryItems =
    profile.role === "enthusiast"
      ? [
          { label: "在售商品", value: `${allProducts.length}` },
          { label: "同城可购", value: `${sameCityCount}` },
          { label: "限时优惠", value: `${discountedCount}` }
        ]
      : [
          { label: "我的货架", value: `${ownedProducts.length}` },
          { label: "同城热卖", value: `${sameCityCount}` },
          { label: "可选品类", value: `${SHOP_CATEGORY_OPTIONS.length - 1}` }
        ];

  return `
    <section class="shop-feature">
      <article class="detail-card shop-hero-card">
        <div class="shop-hero-copy">
          <div>
            <p class="page-label">FitHub Market</p>
            <h3>商城</h3>
          </div>
          <span class="status-pill">正式试运行</span>
        </div>
        <p class="result-tip">${escapeHtml(heroCopy)}</p>
        <div class="shop-summary-grid">
          ${summaryItems
            .map(
              (item) => `
                <div class="shop-summary-item">
                  <span>${escapeHtml(item.label)}</span>
                  <strong>${escapeHtml(item.value)}</strong>
                </div>
              `
            )
            .join("")}
        </div>
      </article>

      <article class="detail-card shop-filter-card">
        <div class="section-title-row">
          <div>
            <h3>分类筛选</h3>
            <p class="result-tip">先按品类看，再决定是打开卖家主页还是直接发消息咨询。</p>
          </div>
          <span class="shop-filter-meta">${escapeHtml(String(filterShopProducts(allProducts).length))} 件</span>
        </div>
        ${renderShopCategoryChips(allProducts)}
      </article>

      ${
        showOwnedSection
          ? `
            <article class="detail-card">
              <div class="section-title-row">
                <div>
                  <h3>我的货架</h3>
                  <p class="result-tip">${ownedProducts.length ? "这里放你当前身份最适合售卖的训练器材、周边和门店商品。" : "你现在还没有上架商品，先看下面的平台选品和同城热卖，后面我们可以继续接上架能力。"}</p>
                </div>
                <span class="shop-filter-meta">${escapeHtml(String(filteredOwned.length))} 件</span>
              </div>
              ${
                filteredOwned.length
                  ? `
                    <div class="shop-product-list">
                      ${filteredOwned.map((item) => renderShopProductCard(item, profile, { owned: true })).join("")}
                    </div>
                  `
                  : '<article class="empty-card">当前筛选下你的货架还没有商品。你可以切换分类看看，或者继续浏览下面的平台精选。</article>'
              }
            </article>
          `
          : ""
      }

      <article class="detail-card">
        <div class="section-title-row">
          <div>
            <h3>${profile.role === "enthusiast" ? "同城热卖" : "平台与同城精选"}</h3>
            <p class="result-tip">${profile.role === "enthusiast" ? "优先展示附近健身房、教练和平台当前适合试运行的商品。" : "你可以先看平台精选和其他卖家的热卖商品，后面再决定自己的货架怎么铺。"}</p>
          </div>
          <span class="shop-filter-meta">${escapeHtml(String(filteredMarketplace.length))} 件</span>
        </div>
        <div class="shop-product-list">
          ${filteredMarketplace.map((item) => renderShopProductCard(item, profile)).join("")}
        </div>
      </article>
    </section>
  `;
}

function renderMyFeaturePage(profile, managedProfiles, feature) {
  const bookings = getRelevantBookingsForProfile(profile);
  const incomingBookings = getIncomingBookings(profile);
  const socialTab = feature === "followers" ? "followers" : state.socialTab || "following";
  const emptyOutgoingBookingMarkup = '<article class="empty-card">你还没有正式预约。去首页、探索或教练/场馆主页完成第一次预约后，这里才会出现记录。</article>';
  const emptyIncomingBookingMarkup = `<article class="empty-card">${profile.role === "coach" ? "暂时还没有学员预约你，完善主页、价格和动态后，这里会出现新的预约消息。" : "暂时还没有用户预约你的场馆，完善主页、价格和设施信息后，这里会出现新的订单。"}</article>`;
  if (feature === "checkin" && state.workoutSession) {
    return `
      <section class="profile-subpage-stack profile-subpage-stack--live">
        ${renderWorkoutSession(profile)}
      </section>
    `;
  }

  const featureMap = {
    account: {
      title: "账户",
      subtitle: "查看当前身份资料与主页信息",
      content: `
        <article class="detail-card">
          <div class="dashboard-profile-row">
            <div class="dashboard-profile-main">
              ${renderAvatarMarkup(profile, "avatar avatar--large")}
              <div>
                <h2>${escapeHtml(profile.name)}</h2>
                <p>${escapeHtml(profile.handle)}</p>
                <span>${escapeHtml(getRoleLabel(profile.role))}</span>
              </div>
            </div>
            <button class="mini-button mini-button--accent" data-edit-role="${profile.role}" type="button">编辑资料</button>
          </div>
          <div class="detail-grid">
            <div class="detail-item">
              <span>所在城市</span>
              <strong>${escapeHtml(profile.city || state.userPosition.city)}</strong>
            </div>
            <div class="detail-item">
              <span>常驻定位</span>
              <strong>${escapeHtml(profile.locationLabel || state.userPosition.label)}</strong>
            </div>
            <div class="detail-item">
              <span>训练等级</span>
              <strong>${escapeHtml(profile.level || "未填写")}</strong>
            </div>
            <div class="detail-item">
              <span>训练目标</span>
              <strong>${escapeHtml(profile.goal || "保持规律训练")}</strong>
            </div>
            <div class="detail-item">
              <span>性别</span>
              <strong>${escapeHtml(profile.gender || "未填写")}</strong>
            </div>
            <div class="detail-item">
              <span>${profile.role === "enthusiast" ? "身高 / 体重" : "所在区域"}</span>
              <strong>${escapeHtml(profile.role === "enthusiast" ? `${profile.heightCm || "--"} cm / ${profile.weightKg || "--"} kg` : profile.locationLabel || state.userPosition.label)}</strong>
            </div>
            ${
              profile.role === "coach"
                ? `
                  <div class="detail-item">
                    <span>课程定价</span>
                    <strong>${escapeHtml(profile.price || "待设置")}</strong>
                  </div>
                  <div class="detail-item">
                    <span>从业时间</span>
                    <strong>${escapeHtml(profile.years ? `${profile.years} 年` : "未填写")}</strong>
                  </div>
                `
                : profile.role === "gym"
                  ? `
                    <div class="detail-item">
                      <span>会员定价</span>
                      <strong>${escapeHtml(profile.price || "待设置")}</strong>
                    </div>
                    <div class="detail-item">
                      <span>营业时间</span>
                      <strong>${escapeHtml(profile.hours || "未填写")}</strong>
                    </div>
                  `
                  : ""
            }
          </div>
        </article>
      `
    },
    checkin: {
      title: "打卡",
      subtitle: "记录跑步、传统力量训练和其他运动项目",
      content: renderCheckinFeature(profile)
    },
    "outdoor-share": {
      title: "户外轨迹",
      subtitle: "像 Keep 或咕咚那样，把户外运动沉淀成一张更有成就感的分享页",
      content: renderOutdoorRouteFeature(profile)
    },
    "outdoor-map": {
      title: "轨迹地图",
      subtitle: "放大查看这次户外运动的真实地图轨迹和定位详情",
      content: renderOutdoorRouteMapDetail(profile)
    },
    orders: {
      title: "订单",
      subtitle: profile.role === "enthusiast" ? "查看最近预约、付款与订单状态" : "查看别人给我的订单、预约和待服务记录",
      content: renderManagedBookingList(profile, bookings, {
        emptyText: profile.role === "enthusiast" ? "你还没有正式预约。去首页、探索或教练/场馆主页完成第一次预约后，这里才会出现记录。" : emptyIncomingBookingMarkup.replace(/<\/?article[^>]*>/g, ""),
        primaryAction: profile.role === "enthusiast" ? "查看主页" : "联系对方"
      })
    },
    favorites: {
      title: "关注",
      subtitle: "这里集中展示你已经关注的人，以及正在关注你的粉丝",
      content: renderSocialProfilesSection(socialTab)
    },
    collections: {
      title: "收藏",
      subtitle: "把探索和动态里喜欢的视频、图片与训练干货收进这里，方便反复查看",
      content: renderCollectionsFeature()
    },
    shop: {
      title: "商城",
      subtitle: "购买、售卖或管理运动器材、周边与平台商品",
      content: renderShopFeature(profile)
    },
    followers: {
      title: "粉丝",
      subtitle: "查看已经关注你的用户、教练和健身房",
      content: renderSocialProfilesSection("followers")
    },
    points: {
      title: "积分",
      subtitle: "由预约和打卡累积的成长积分",
      content: `
        <article class="summary-card">
          <div>
            <span>当前积分</span>
            <strong>${getProfilePoints(profile, bookings)}</strong>
          </div>
          <div>
            <span>本周打卡</span>
            <strong>${getWeeklyCheckins(profile).length}</strong>
          </div>
          <div>
            <span>已预约</span>
            <strong>${bookings.length}</strong>
          </div>
        </article>
        <article class="detail-card">
          <div class="detail-grid">
            <div class="detail-item"><span>积分来源</span><strong>每次打卡 +12</strong></div>
            <div class="detail-item"><span>预约完成</span><strong>每单 +18</strong></div>
            <div class="detail-item"><span>当前状态</span><strong>${getProfilePoints(profile, bookings) ? "持续积累中" : "还未开始"}</strong></div>
          </div>
        </article>
      `
    },
    schedule: {
      title: "预约",
      subtitle: profile.role === "enthusiast" ? "查看你的课程排期与待上课记录" : "查看别人对你的预约、待接待和服务排期",
      content: renderManagedBookingList(profile, profile.role === "enthusiast" ? bookings : incomingBookings, {
        emptyText: profile.role === "enthusiast" ? emptyOutgoingBookingMarkup.replace(/<\/?article[^>]*>/g, "") : emptyIncomingBookingMarkup.replace(/<\/?article[^>]*>/g, ""),
        primaryAction: profile.role === "enthusiast" ? "查看主页" : "查看预约"
      })
    },
    health: {
      title: "健康",
      subtitle: "查看数据中心、趋势变化与设备同步状态",
      content: renderHealthFeature(profile)
    },
    reviews: {
      title: "评分",
      subtitle: profile.role === "enthusiast" ? "训练者当前不展示公开评分" : "查看用户给你的评分与评价",
      content: renderReviewsFeature(profile)
    },
    messages: {
      title: "消息",
      subtitle: "查看别人给你的赞、评论、@和私信咨询",
      content: renderMessagesFeature(profile)
    },
    moments: {
      title: "我的动态",
      subtitle: "按时间从近到远查看你自己发布的健身圈内容",
      content: renderPersonalMoments(profile)
    }
  };

  const currentFeature = featureMap[feature] || featureMap.account;
  const showFeatureIntro = !["checkin", "health"].includes(feature);

  return `
    <section class="page-header">
      <div>
        <p class="page-label">My</p>
        <h1>${escapeHtml(currentFeature.title)}</h1>
      </div>
      <button class="mini-button" data-open-my-home="1" type="button">我的</button>
    </section>

    <article class="swipe-tip">
      <div class="swipe-tip-copy">
        <span class="swipe-tip-mark"></span>
        <span>从左边缘右滑，快速返回我的主页</span>
      </div>
      <button class="text-link" data-back-profile="1" type="button">返回</button>
    </article>

    <section class="managed-strip managed-strip--dashboard">
      ${managedProfiles
        .map(
          (item) => `
            <button class="managed-chip ${item.id === profile.id ? "is-active" : ""}" data-switch-managed="${item.id}" type="button">
              ${escapeHtml(getRoleLabel(item.role))}
            </button>
          `
        )
        .join("")}
    </section>

    ${
      showFeatureIntro
        ? `
          <article class="helper-card helper-card--my-feature">
            <strong>${escapeHtml(currentFeature.title)}</strong>
            <p>${escapeHtml(currentFeature.subtitle)}</p>
          </article>
        `
        : ""
    }

    <section class="profile-subpage-stack">
      ${currentFeature.content}
    </section>
  `;
}

function renderProfilePage(profile) {
  const managedProfiles = getManagedProfiles();
  const managed = isManagedProfile(profile.id);
  const followed = state.followSet.has(profile.id);
  const draftRate = Number(state.ratingDrafts[profile.id] || 0);
  const draftReview = state.reviewDrafts[profile.id] || "";
  const returnLabel = getProfileReturnLabel();

  if (managed && profile.id === getMyPageProfile()?.id) {
    if (state.profileSubpage) {
      return renderMyFeaturePage(profile, managedProfiles, state.profileSubpage);
    }
    return renderPersonalDashboardPage(profile, managedProfiles);
  }

  return `
    <section class="page-header">
      <div>
        <p class="page-label">Profile</p>
        <h1>主页</h1>
      </div>
      <button class="mini-button" data-open-role-picker="1" type="button">我是${escapeHtml(roleConfig[state.selectedRole].short)}</button>
    </section>

    <article class="swipe-tip">
      <div class="swipe-tip-copy">
        <span class="swipe-tip-mark"></span>
        <span>从左边缘右滑，快速返回${escapeHtml(returnLabel)}</span>
      </div>
      <button class="text-link" data-back-profile="1" type="button">返回</button>
    </article>

    <section class="managed-strip">
      ${managedProfiles
        .map(
          (item) => `
            <button class="managed-chip ${item.id === profile.id ? "is-active" : ""}" data-switch-managed="${item.id}" type="button">
              ${escapeHtml(getRoleLabel(item.role))}
            </button>
          `
        )
        .join("")}
    </section>

    <article class="profile-hero">
      <div class="profile-cover image-shell image-shell--cover">
        ${
          getProfileCoverImage(profile)
            ? `<img class="profile-cover-image" src="${optimizeRemoteImageUrl(getProfileCoverImage(profile), "cover")}" alt="${escapeHtml(profile.name)}封面图" loading="lazy" decoding="async">`
            : ""
        }
      </div>
      <div class="profile-hero-content">
        ${renderAvatarMarkup(profile, "avatar avatar--large")}
        <div class="profile-heading">
          <div class="profile-title-row">
            <h2>${escapeHtml(profile.name)}</h2>
            <span class="role-badge">${escapeHtml(getRoleLabel(profile.role))}</span>
          </div>
          <p class="profile-handle">${escapeHtml(profile.handle)}</p>
          <p class="profile-bio">${escapeHtml(profile.bio)}</p>
          <div class="profile-tags">
            ${profile.tags.map((tag) => `<span>${escapeHtml(tag)}</span>`).join("")}
          </div>
          <div class="profile-stats">
            <div><strong>${profile.followers}</strong><span>关注者</span></div>
            <div><strong>${profile.following}</strong><span>关注中</span></div>
            <div><strong>${profile.role === "enthusiast" ? "--" : getRatingDisplay(profile)}</strong><span>${profile.role === "enthusiast" ? "训练状态" : "评分"}</span></div>
          </div>
          <div class="community-meta community-meta--profile">
            <span>${escapeHtml(profile.locationLabel)}</span>
            ${profile.price ? `<span>${escapeHtml(profile.price)}</span>` : ""}
            ${profile.role !== "enthusiast" ? `<span>${profile.ratingCount ? `${profile.ratingCount} 条评分` : "还没有评分"}</span>` : ""}
          </div>
          <div class="profile-actions">
            ${
              managed
                ? `<button class="mini-button mini-button--accent" data-edit-role="${profile.role}" type="button">编辑资料</button>`
                : `<button class="follow-button ${followed ? "is-active" : ""}" data-toggle-follow="${profile.id}" type="button">${followed ? "已关注" : "关注"}</button>`
            }
            ${
              !managed && followed
                ? `<button class="mini-button" data-open-chat="${profile.id}" type="button">私信</button>`
                : ""
            }
            ${
              !managed && profile.role !== "enthusiast"
                ? `<button class="mini-button" data-create-booking="${profile.id}" type="button">预约</button>`
                : ""
            }
          </div>
        </div>
      </div>
    </article>

    <section class="section-title-row">
      <h3>主页动态</h3>
      <button class="text-link" data-open-profile="${profile.id}" type="button">刷新</button>
    </section>

    ${renderProfileFeatureSection(profile)}

    ${renderProfileTimeline(profile)}

    ${
      profile.role !== "enthusiast"
        ? `
          <article class="rating-card">
            <div class="section-title-row">
              <h3>用户评分</h3>
              <span class="score-pill">${profile.ratingCount ? `${profile.ratingAvg.toFixed(1)} / 5` : "新入驻"}</span>
            </div>
            <p class="rating-desc">健身爱好者可以给教练和健身房评分，评分会同步展示到搜索卡片和主页。</p>
            ${renderRatingStars(profile.id, draftRate)}
            <textarea class="review-input" data-review-input="${profile.id}" placeholder="写一句你的体验评价">${escapeHtml(draftReview)}</textarea>
            <button class="primary-submit" data-submit-rating="${profile.id}" type="button">提交评分</button>
            <section class="review-list">
              ${profile.reviews
                .map(
                  (review) => `
                    <article class="review-card">
                      <div class="review-head">
                        <strong>${escapeHtml(review.author)}</strong>
                        <span>★ ${review.score} · ${escapeHtml(review.time)}</span>
                      </div>
                      <p>${escapeHtml(review.text)}</p>
                    </article>
                  `
                )
                .join("")}
            </section>
          </article>
        `
        : ""
    }
  `;
}

function renderProfile() {
  const profile = getProfile(state.activeProfileId) || getMyPageProfile() || getCurrentActor();

  if (!profile) {
    appView.innerHTML = `
      <section class="page-header">
        <div>
          <p class="page-label">Profile</p>
          <h1>主页</h1>
        </div>
      </section>
      <article class="empty-card">先完成身份注册，就会自动生成对应主页。</article>
    `;
    return;
  }

  appView.innerHTML = renderProfilePage(profile);
}

function maskPhone(phone = "") {
  const normalized = normalizePhone(phone);
  if (normalized.length < 7) return normalized || "未保存手机号";
  return `${normalized.slice(0, 3)}****${normalized.slice(-4)}`;
}

function renderWelcomeOverlay() {
  const canLogout = Boolean(state.managedProfileIds.length || getStoredAccounts().length);
  return `
    <div class="overlay-backdrop" data-close-overlay="1"></div>
    <div class="overlay-panel overlay-panel--welcome">
      <div class="overlay-head">
        <div>
          <p class="page-label">欢迎进入</p>
          <h2>你当前更像哪种身份？</h2>
          <p>先选择自己的身份，接下来注册流程和首页推荐都会更贴近你的使用方式。</p>
        </div>
        <button class="close-button" data-close-overlay="1" type="button">×</button>
      </div>
      <div class="welcome-grid">
        ${Object.entries(roleConfig)
          .map(
            ([key, role]) => `
              <button class="welcome-card ${key === state.selectedRole ? "is-active" : ""}" data-choose-role="${key}" type="button">
                <strong>${role.label}${hasManagedRole(key) ? " · 已注册" : ""}</strong>
                <p>${role.intro}</p>
              </button>
            `
          )
          .join("")}
      </div>
      <div class="action-row">
        <button class="mini-button" ${canLogout ? 'data-logout-account="1"' : 'data-close-overlay="1"'} type="button">退出登录</button>
        <button class="mini-button mini-button--accent" data-open-auth="${escapeHtml(state.selectedRole)}" type="button">登录已有账户</button>
      </div>
    </div>
  `;
}

function renderAuthOverlay() {
  const storedAccounts = getStoredAccounts();
  const matchedRoleSet = new Set(state.authMatches.map((item) => item.role));

  return `
    <div class="overlay-backdrop" data-close-overlay="1"></div>
    <div class="overlay-panel overlay-panel--register">
      <div class="overlay-head">
        <div>
          <p class="page-label">账户登录</p>
          <h2>找回你的账号</h2>
          <p>这个设备有历史凭证时会优先自动恢复；换设备时，输入手机号后会识别这个手机号下已注册的所有身份。</p>
        </div>
        <button class="close-button" data-close-overlay="1" type="button">×</button>
      </div>

      <div class="role-selector">
        ${Object.entries(roleConfig)
          .map(
            ([key, config]) => `
              <button class="role-option ${key === state.authRole ? "is-active" : ""}" data-auth-role="${key}" type="button">
                <strong>${config.label}</strong>
                <span>${matchedRoleSet.has(key) ? "已识别" : config.short}</span>
              </button>
            `
          )
          .join("")}
      </div>

      ${
        storedAccounts.length
          ? `
            <div class="helper-inline">
              <span>这个设备已记住 ${storedAccounts.length} 个账号</span>
            </div>
            <div class="managed-strip">
              ${storedAccounts
                .map(
                  (account) => {
                    const displayRole = account.roles.includes(state.authRole) ? state.authRole : account.roles[0] || state.authRole;
                    const isActive =
                      account.id === state.authAccountId ||
                      (account.phone === normalizePhone(state.authPhone) && account.roles.includes(state.authRole));

                    return `
                    <button
                      class="managed-chip ${isActive ? "is-active" : ""}"
                      data-quick-login-role="${displayRole}"
                      data-quick-login-account-id="${account.id}"
                      data-quick-login-restore-token="${account.restoreToken}"
                      data-quick-login-phone="${account.phone}"
                      type="button"
                    >
                      ${escapeHtml(roleConfig[displayRole].label)} · ${escapeHtml(maskPhone(account.phone))}
                    </button>
                  `;
                  }
                )
                .join("")}
            </div>
          `
          : ""
      }

      <form class="register-form" id="authForm">
        <label class="form-field">
          <span>手机号 ${state.authAccountId ? "（可选，当前会优先用本机凭证恢复）" : "*"}</span>
          <input data-auth-phone="1" name="phone" type="tel" value="${escapeHtml(state.authPhone)}" placeholder="${escapeHtml(state.authAccountId ? "本机已保存账户凭证，也可以补填手机号" : "请输入注册时填写的手机号")}" ${state.authAccountId ? "" : "required"}>
        </label>
        ${renderAuthVerificationField()}
        ${
          state.authMatches.length
            ? `
              <div class="helper-inline">
                <span>这个手机号下已识别到 ${state.authMatches.length} 个身份</span>
              </div>
              <div class="managed-strip managed-strip--matches">
                ${state.authMatches
                  .map(
                    (item) => `
                      <button
                        class="managed-chip ${item.role === state.authRole ? "is-active" : ""}"
                        data-auth-match-role="${escapeHtml(item.role)}"
                        type="button"
                      >
                        ${escapeHtml(roleConfig[item.role].label)} · ${escapeHtml(item.name)}
                      </button>
                    `
                  )
                  .join("")}
              </div>
            `
            : ""
        }
        <button class="primary-submit" type="submit">${isSmsVerificationEnabled() ? "验证码登录" : "登录这个身份"}</button>
        ${
          state.authMessage
            ? `<p class="helper-note">${escapeHtml(state.authMessage)}</p>`
            : `<p class="helper-note">${isSmsVerificationEnabled() ? "同一设备后续会自动恢复；换设备时，请输入手机号并用短信验证码登录。" : "如果这个设备注册过账号，后面会优先自动恢复；换设备时，输入手机号后会自动识别可登录的身份。"}</p>`
        }
        <button class="text-link" data-open-register-from-auth="${escapeHtml(state.authRole)}" type="button">还没有账号？去注册</button>
      </form>
    </div>
  `;
}

function renderCityOverlay() {
  return `
    <div class="overlay-backdrop" data-close-overlay="1"></div>
    <div class="overlay-panel">
      <div class="overlay-head">
        <div>
          <p class="page-label">城市定位</p>
          <h2>切换顶部城市</h2>
          <p>默认先定位到厦门。你可以改成自己的城市，或使用实时定位。</p>
        </div>
        <button class="close-button" data-close-overlay="1" type="button">×</button>
      </div>
      <div class="city-chip-row">
        ${Object.values(CITY_PRESETS)
          .map(
            (preset) => `
              <button class="city-chip ${preset.city === state.userPosition.city ? "is-active" : ""}" data-city-preset="${preset.key}" type="button">
                ${preset.city}
              </button>
            `
          )
          .join("")}
      </div>
      <label class="form-field form-field--spaced">
        <span>手动输入城市</span>
        <input data-city-input="1" type="text" value="${escapeHtml(state.cityInput)}" placeholder="例如：杭州">
      </label>
      <div class="action-row">
        <button class="mini-button" data-action="locate" type="button">使用我的位置</button>
        <button class="mini-button mini-button--accent" data-apply-manual-city="1" type="button">应用城市</button>
      </div>
      <p class="helper-note">正式版接入高德 / Google Maps 后，这里会支持地图选点和自动逆地理编码。</p>
    </div>
  `;
}

function renderRegisterOverlay() {
  const role = roleConfig[state.registerRole];
  const seed = getRegistrationSeed(state.registerRole);
  seedRegisterDraft(state.registerRole);

  return `
    <div class="overlay-backdrop" data-close-overlay="1"></div>
    <div class="overlay-panel overlay-panel--register">
      <div class="overlay-head">
        <div>
          <p class="page-label">注册 / 入驻</p>
          <h2>${role.label}</h2>
          <p>提交后会自动生成对应主页，健身房和教练也会进入附近搜索与社区流展示。</p>
        </div>
        <button class="close-button" data-close-overlay="1" type="button">×</button>
      </div>

      <div class="role-selector">
        ${Object.entries(roleConfig)
          .map(
            ([key, config]) => `
              <button class="role-option ${key === state.registerRole ? "is-active" : ""}" data-register-role="${key}" type="button">
                <strong>${config.label}</strong>
                <span>${config.short}</span>
              </button>
            `
          )
          .join("")}
      </div>

      <div class="helper-inline">
        <span>当前城市：${escapeHtml(state.userPosition.label)}</span>
        <button class="mini-button" data-open-city="1" type="button">切换城市</button>
      </div>

      <form class="register-form" id="registerForm">
        ${role.fields
          .flatMap((field) => {
            if (field.name === "phone") {
              return [renderField(field, seed), renderRegisterVerificationField()];
            }
            return [renderField(field, seed)];
          })
          .join("")}
        <button class="primary-submit" type="submit">提交${role.label}资料</button>
        ${
          state.registerSuccess
            ? `<p class="success-note">${escapeHtml(state.registerSuccess)}</p>`
            : `<p class="helper-note">${isSmsVerificationEnabled() ? "正式模式下会先校验手机号验证码，再创建或更新你的身份主页。" : "演示版会直接生成主页；正式版可接入验证码、地图选点、图片上传和审核流。"}</p>`
        }
        <button class="text-link" data-open-auth="${escapeHtml(state.registerRole)}" type="button">已有账号？去登录</button>
      </form>
    </div>
    ${renderRegisterWheelSheet()}
  `;
}

function renderComposeOverlay() {
  const managedProfiles = getManagedProfiles();
  const activeProfile = getProfile(state.composeProfileId) || managedProfiles[0];

  return `
    <div class="overlay-backdrop" data-close-overlay="1"></div>
    <div class="overlay-panel overlay-panel--compose">
      <form class="compose-form" id="composeForm">
        <div class="compose-nav">
          <button class="compose-nav-button" data-close-overlay="1" type="button">取消</button>
          <strong>发布动态</strong>
          <button class="compose-submit-top" type="submit">发布</button>
        </div>

        <div class="compose-author">
          ${renderAvatarMarkup(activeProfile || { avatar: "?" }, "avatar")}
          <div>
            <strong>${escapeHtml(activeProfile?.name || "未选择身份")}</strong>
            <p>${escapeHtml(state.userPosition.label)}</p>
          </div>
        </div>

        <div class="compose-profile-row">
          ${managedProfiles
            .map(
              (profile) => `
                <button class="compose-chip ${profile.id === state.composeProfileId ? "is-active" : ""}" data-compose-profile="${profile.id}" type="button">
                  ${renderAvatarMarkup(profile, "compose-chip-avatar")}
                  <span>${escapeHtml(profile.name)}</span>
                </button>
              `
            )
            .join("")}
        </div>

        <textarea data-compose-content="1" class="compose-input" placeholder="这一刻你想分享什么？训练、门店动态、空闲档期都可以...">${escapeHtml(state.composeContent)}</textarea>

        <div class="compose-tools">
          <label class="compose-tool">
            <input data-compose-media-input="1" type="file" accept="image/*" multiple hidden>
            <span>图片</span>
          </label>
          <label class="compose-tool">
            <input data-compose-media-input="1" type="file" accept="video/*" multiple hidden>
            <span>视频</span>
          </label>
        </div>

        ${
          state.composeMedia.length
            ? `
              <div class="compose-preview-grid">
                ${state.composeMedia
                  .map((item, index) => {
                    if (item.type === "video") {
                      return `
                        <div class="compose-preview-card image-shell image-shell--cover is-loaded">
                          <button class="compose-preview-remove" data-remove-compose-media-index="${index}" type="button" aria-label="移除这个视频">×</button>
                          <video class="compose-preview-video" src="${getMediaDisplayUrl(item)}" poster="${escapeHtml(getMediaThumbnailUrl(item, "feed"))}" controls playsinline preload="metadata"></video>
                          <span class="compose-preview-label">视频</span>
                        </div>
                      `;
                    }

                    return `
                      <div class="compose-preview-card image-shell image-shell--cover is-loaded">
                        <button class="compose-preview-remove" data-remove-compose-media-index="${index}" type="button" aria-label="移除这张图片">×</button>
                        <img class="compose-preview-image" src="${escapeHtml(getMediaThumbnailUrl(item, "feed"))}" alt="${escapeHtml(item.name || "预览图")}" loading="lazy" decoding="async">
                        <span class="compose-preview-label">图片</span>
                      </div>
                    `;
                  })
                  .join("")}
              </div>
            `
            : ""
        }
        <div class="compose-footer-note">将发布到 ${escapeHtml(activeProfile?.name || "")} 的主页动态流</div>
      </form>
    </div>
  `;
}

function renderMediaDetailOverlay() {
  const entry = getMediaViewerEntry();
  if (!entry) {
    return `
      <div class="overlay-backdrop" data-close-overlay="1"></div>
      <div class="overlay-panel overlay-panel--media">
        <div class="overlay-head">
          <div>
            <p class="page-label">媒体详情</p>
            <h2>内容不存在</h2>
          </div>
          <button class="close-button" data-close-overlay="1" type="button">×</button>
        </div>
      </div>
    `;
  }

  const { profile, post, item, index, total } = entry;
  const canGoPrev = index > 0;
  const canGoNext = index < total - 1;
  const profileName = profile?.name || "FitHub 用户";
  const authorMeta = [profile?.handle, post.time].filter(Boolean).join(" · ");
  const detailUrl = getMediaDisplayUrl(item);
  const detailTypeLabel = item.type === "video" ? "视频" : "图片";
  const detailSizeLabel = formatMediaSize(item.sizeBytes);

  return `
    <div class="overlay-backdrop" data-close-overlay="1"></div>
    <div class="overlay-panel overlay-panel--media">
      <div class="overlay-head overlay-head--media">
        <div>
          <p class="page-label">媒体详情</p>
          <h2>${escapeHtml(profileName)}</h2>
          <p>${escapeHtml(authorMeta)}</p>
        </div>
        <button class="close-button" data-close-overlay="1" type="button">×</button>
      </div>

      <section class="media-detail-shell">
        <div class="media-detail-stage image-shell image-shell--cover is-loaded">
          ${
            item.type === "video"
              ? `<video class="media-detail-video" src="${getMediaDisplayUrl(item)}" poster="${escapeHtml(getMediaThumbnailUrl(item, "detail"))}" controls playsinline preload="metadata"></video>`
              : `<img class="media-detail-image" src="${escapeHtml(getMediaDisplayUrl(item) || getMediaThumbnailUrl(item, "detail"))}" alt="${escapeHtml(item.name || "媒体详情")}" decoding="async">`
          }
          ${
            total > 1
              ? `
                <div class="media-detail-stage-actions">
                  <button class="media-nav-button" data-shift-media-index="-1" type="button" ${canGoPrev ? "" : "disabled"}>上一张</button>
                  <span class="media-detail-counter">${index + 1} / ${total}</span>
                  <button class="media-nav-button" data-shift-media-index="1" type="button" ${canGoNext ? "" : "disabled"}>下一张</button>
                </div>
              `
              : `<div class="media-detail-stage-actions"><span class="media-detail-counter">1 / 1</span></div>`
          }
        </div>

        <div class="media-detail-meta">
          ${
            profile
              ? `
                <button class="media-detail-author" data-open-profile="${profile.id}" type="button">
                  ${renderAvatarMarkup(profile, "avatar")}
                  <div>
                    <strong>${escapeHtml(profileName)}</strong>
                    <p>${escapeHtml(getRoleLabel(profile.role))} · ${escapeHtml(profile.locationLabel || profile.city || "FitHub")}</p>
                  </div>
                </button>
              `
              : ""
          }
          <div class="media-detail-copy">
            <p>${escapeHtml(post.content || "分享了一条新的媒体动态。")}</p>
            <small>${escapeHtml(post.meta || "")}</small>
          </div>
          <div class="media-detail-actions">
            <div class="media-detail-badges">
              <span class="media-detail-pill">${escapeHtml(detailTypeLabel)}</span>
              ${detailSizeLabel ? `<span class="media-detail-pill">${escapeHtml(detailSizeLabel)}</span>` : ""}
              ${item.storageProvider === "supabase" ? '<span class="media-detail-pill media-detail-pill--accent">云端已保存</span>' : ""}
            </div>
            ${
              detailUrl
                ? `<a class="mini-button media-detail-link" href="${escapeHtml(detailUrl)}" target="_blank" rel="noreferrer">${item.type === "video" ? "打开视频" : "打开原图"}</a>`
                : ""
            }
          </div>
          <div class="media-detail-stats">
            <span>${escapeHtml(`${post.likeCount || 0} 赞`)}</span>
            <span>${escapeHtml(`${post.favoriteCount || 0} 收藏`)}</span>
            <span>${escapeHtml(`${post.comments?.length || 0} 评论`)}</span>
          </div>
        </div>

        ${
          total > 1
            ? `
              <div class="media-detail-strip">
                ${post.media
                  .map((mediaItem, mediaIndex) => `
                    <button
                      class="media-detail-thumb ${mediaIndex === index ? "is-active" : ""}"
                      data-open-media-detail="${post.id}"
                      data-media-index="${mediaIndex}"
                      type="button"
                    >
                      ${
                        mediaItem.type === "video"
                          ? `<img src="${escapeHtml(getMediaThumbnailUrl(mediaItem, "thumb"))}" alt="${escapeHtml(mediaItem.name || "视频缩略图")}" decoding="async">`
                          : `<img src="${escapeHtml(getMediaThumbnailUrl(mediaItem, "thumb"))}" alt="${escapeHtml(mediaItem.name || "图片缩略图")}" decoding="async">`
                      }
                    </button>
                  `)
                  .join("")}
              </div>
            `
            : ""
        }
      </section>
    </div>
  `;
}

function renderChatOverlay() {
  const targetProfile = getProfile(state.chatTargetProfileId);
  const thread = getThreadForProfile(state.chatTargetProfileId);
  const isSendingChat = state.pendingMessageProfileIds.has(state.chatTargetProfileId);
  const canSendChat = Boolean(state.chatDraft.trim());

  if (!targetProfile) {
    return `
      <div class="overlay-backdrop" data-close-overlay="1"></div>
      <div class="overlay-panel overlay-panel--chat">
        <div class="overlay-head">
          <div>
            <p class="page-label">私信</p>
            <h2>聊天对象不存在</h2>
          </div>
          <button class="close-button" data-close-overlay="1" type="button">×</button>
        </div>
      </div>
    `;
  }

  return `
    <div class="overlay-backdrop" data-close-overlay="1"></div>
    <div class="overlay-panel overlay-panel--chat">
      <div class="overlay-head">
        <div>
          <p class="page-label">私信</p>
          <h2>${escapeHtml(targetProfile.name)}</h2>
          <p>已关注后可继续沟通预约、课程和训练安排。</p>
        </div>
        <button class="close-button" data-close-overlay="1" type="button">×</button>
      </div>

      <section class="chat-thread">
        ${
          thread?.messages?.length
            ? thread.messages
                .map(
                  (message) => {
                    const isSelf = message.senderProfileId === state.currentActorProfileId;
                    const bubbleProfile = isSelf
                      ? getMyPageProfile()
                      : targetProfile;
                    return `
                      <article class="chat-row ${isSelf ? "chat-row--self" : ""}">
                        ${!isSelf ? renderAvatarMarkup(bubbleProfile || { name: message.senderName }, "chat-avatar") : ""}
                        <div class="chat-stack ${isSelf ? "chat-stack--self" : ""}">
                          <div class="chat-bubble ${isSelf ? "is-self" : ""}">
                            <p>${escapeHtml(message.text)}</p>
                          </div>
                          <span class="chat-time">${escapeHtml(message.time)}</span>
                        </div>
                        ${isSelf ? renderAvatarMarkup(bubbleProfile || { name: message.senderName }, "chat-avatar") : ""}
                      </article>
                    `;
                  }
                )
                .join("")
            : '<article class="empty-card">还没有聊天记录，先发一句打招呼吧。</article>'
        }
      </section>

      <form class="chat-form ${isSendingChat ? "is-sending" : ""}" id="chatForm">
        <input data-chat-input="1" type="text" value="${escapeHtml(state.chatDraft)}" placeholder="输入私信内容，约课或咨询都可以">
        <button class="compose-submit-top" type="submit" ${canSendChat ? "" : "disabled"}>发送</button>
      </form>
    </div>
  `;
}

function renderFollowingOverlay() {
  const mode = state.socialTab || "following";
  const profiles = mode === "followers" ? getFollowerProfiles() : getFollowedProfiles();
  const heading = mode === "followers" ? "我的粉丝" : "我关注的";
  const description = mode === "followers"
    ? "这里会显示当前身份的粉丝，点一下就能直接回关。"
    : "这里会显示你当前身份已经关注的健身房、教练和训练搭子。";

  return `
    <div class="overlay-backdrop" data-close-overlay="1"></div>
    <div class="overlay-panel overlay-panel--following">
      <div class="overlay-head overlay-head--following">
        <div>
          <p class="page-label">Following</p>
          <h2>${heading}</h2>
          <p>${description}</p>
        </div>
        <button class="close-button" data-close-overlay="1" type="button">×</button>
      </div>

      <div class="following-tabs">
        <button class="following-tab ${mode === "following" ? "is-active" : ""}" data-set-social-tab="following" type="button">我关注的</button>
        <button class="following-tab ${mode === "followers" ? "is-active" : ""}" data-set-social-tab="followers" type="button">我的粉丝</button>
        <span class="following-count">${profiles.length} 个对象</span>
      </div>

      <section class="following-list">
        ${
          profiles.length
            ? profiles
                .map((profile) => {
                  const metaLine = [profile.city, profile.locationLabel || profile.location, `${profile.followers || 0} 粉丝`]
                    .filter(Boolean)
                    .join(" · ");
                  const summary = profile.shortDesc || profile.bio || `${profile.name} 的主页`;

                  return `
                    <article class="following-row" data-open-profile="${profile.id}">
                      <div class="following-row-main">
                        ${renderAvatarMarkup(profile, "avatar avatar--following")}
                        <div class="following-copy">
                          <div class="following-name-row">
                            <strong>${escapeHtml(profile.name)}</strong>
                            <span>${escapeHtml(getRoleLabel(profile.role))}</span>
                          </div>
                          <p class="following-handle">${escapeHtml(profile.handle || `@${profile.id}`)}</p>
                          <p class="following-summary">${escapeHtml(summary)}</p>
                          <small>${escapeHtml(metaLine)}</small>
                        </div>
                      </div>
                      ${
                        mode === "following"
                          ? ""
                          : state.followSet.has(profile.id)
                            ? '<button class="follow-button is-reciprocal following-action" type="button" disabled>已回关</button>'
                            : `<button class="follow-button following-action" data-follow-back="${profile.id}" type="button">回关</button>`
                      }
                    </article>
                  `;
                })
                .join("")
            : `
              <article class="empty-card">
                ${mode === "followers" ? "暂时还没有粉丝，继续完善主页、发布动态和接收预约后，这里会慢慢热闹起来。" : "你还没有关注任何对象。先在探索页上方点几个感兴趣的健身房、教练或用户，这里就会立刻显示出来。"}
              </article>
            `
        }
      </section>
    </div>
  `;
}

function renderOverlay() {
  if (!state.overlayMode) {
    overlay.hidden = true;
    overlay.innerHTML = "";
    return;
  }

  overlay.hidden = false;

  if (state.overlayMode === "welcome") overlay.innerHTML = renderWelcomeOverlay();
  if (state.overlayMode === "auth") overlay.innerHTML = renderAuthOverlay();
  if (state.overlayMode === "city") overlay.innerHTML = renderCityOverlay();
  if (state.overlayMode === "register") overlay.innerHTML = renderRegisterOverlay();
  if (state.overlayMode === "compose") overlay.innerHTML = renderComposeOverlay();
  if (state.overlayMode === "media") overlay.innerHTML = renderMediaDetailOverlay();
  if (state.overlayMode === "chat") overlay.innerHTML = renderChatOverlay();
  if (state.overlayMode === "following") overlay.innerHTML = renderFollowingOverlay();
  hydrateAsyncImages(overlay);
  if (state.overlayMode === "register" && state.registerWheelField) {
    initializeRegisterWheelPicker();
  }
}

function syncChatComposerState() {
  const chatForm = overlay.querySelector("#chatForm");
  if (!chatForm) return;
  const input = chatForm.querySelector('[data-chat-input="1"]');
  const submit = chatForm.querySelector('button[type="submit"]');
  const isSendingChat = state.pendingMessageProfileIds.has(state.chatTargetProfileId);
  const canSendChat = Boolean((state.chatDraft || "").trim());
  if (input) {
    input.disabled = false;
  }
  if (submit) {
    submit.disabled = !canSendChat;
    submit.textContent = "发送";
  }
  if (chatForm) {
    chatForm.classList.toggle("is-sending", isSendingChat);
  }
}

function renderPage() {
  resetProfileSwipe();
  routeMapRegistry.clear();
  document.body.classList.toggle(
    "is-workout-live",
    state.activePage === "profile" && state.profileSubpage === "checkin" && Boolean(state.workoutSession)
  );
  appView.dataset.page = state.activePage;
  if (state.isBootstrapping) {
    appView.innerHTML = `
      <section class="page-header">
        <div>
          <p class="page-label">FitHub</p>
          <h1>正在连接试用服务</h1>
        </div>
      </section>
      <article class="empty-card">正在同步共享数据、身份和互动内容，请稍候...</article>
    `;
    syncNavActive();
    return;
  }
  if (state.activePage === "home") renderHome();
  if (state.activePage === "discover") renderDiscover();
  if (state.activePage === "booking") renderBooking();
  if (state.activePage === "profile") renderProfile();
  syncNavActive();
  renderOverlay();
  hydrateAsyncImages(appView);
  hydrateRouteMaps(appView).catch(() => {});
}

appView.addEventListener("click", (event) => {
  const target = event.target.closest("button, article");
  if (!target) return;

  if (target.dataset.openCity) {
    openCitySelector();
    return;
  }

  if (target.dataset.openRolePicker) {
    openOverlay("welcome");
    return;
  }

  if (target.dataset.logoutAccount) {
    runTask(() => logoutCurrentDevice());
    return;
  }

  if (target.dataset.openFollowing) {
    state.socialTab = "following";
    openOverlay("following");
    return;
  }

  if (target.dataset.openFollowers) {
    state.socialTab = "followers";
    openOverlay("following");
    return;
  }

  if (target.dataset.action === "locate") {
    requestCurrentLocation();
    return;
  }

  if (target.dataset.action === "register") {
    openRegister(state.selectedRole);
    return;
  }

  if (target.dataset.homeTab) {
    state.activeHomeTab = target.dataset.homeTab;
    renderPage();
    return;
  }

  if (target.dataset.openProfile) {
    openProfile(target.dataset.openProfile);
    return;
  }

  if (target.dataset.openMediaDetail) {
    openMediaViewer(target.dataset.openMediaDetail, Number(target.dataset.mediaIndex || 0));
    return;
  }

  if (target.dataset.openMyHome) {
    openMyPage();
    return;
  }

  if (target.dataset.openMyFeature) {
    const myProfile = getMyPageProfile();
    if (!myProfile) return;
    if (target.dataset.openMyFeature === "favorites") {
      state.socialTab = "following";
    }
    if (target.dataset.openMyFeature === "followers") {
      state.socialTab = "followers";
    }
    if (target.dataset.openMyFeature === "health") {
      state.healthViewMode = "overview";
    }
    if (target.dataset.openMyFeature === "shop") {
      state.shopCategory = "all";
    }
    if (target.dataset.openMyFeature === "messages") {
      markNotificationsRead(myProfile.id);
    }
    state.activePage = "profile";
    state.activeProfileId = myProfile.id;
    state.profileSubpage = target.dataset.openMyFeature;
    syncNavActive();
    renderPage();
    appView.scrollTop = 0;
    return;
  }

  if (target.dataset.openRouteShare) {
    const myProfile = getMyPageProfile();
    if (!myProfile) return;
    state.activePage = "profile";
    state.activeProfileId = myProfile.id;
    state.profileSubpage = "outdoor-share";
    state.outdoorShareCheckinId = target.dataset.openRouteShare;
    syncNavActive();
    renderPage();
    appView.scrollTop = 0;
    return;
  }

  if (target.dataset.openRouteMapDetail) {
    const myProfile = getMyPageProfile();
    if (!myProfile) return;
    state.activePage = "profile";
    state.activeProfileId = myProfile.id;
    state.profileSubpage = "outdoor-map";
    state.outdoorShareCheckinId = target.dataset.openRouteMapDetail;
    syncNavActive();
    renderPage();
    appView.scrollTop = 0;
    return;
  }

  if (target.dataset.setHealthView) {
    state.healthViewMode = target.dataset.setHealthView;
    renderPage();
    return;
  }

  if (target.dataset.shopCategory) {
    state.shopCategory = target.dataset.shopCategory;
    renderPage();
    return;
  }

  if (target.dataset.backProfile) {
    goBackFromProfile();
    return;
  }

  if (target.dataset.goBooking) {
    state.activePage = "booking";
    syncNavActive();
    renderPage();
    appView.scrollTop = 0;
    return;
  }

  if (target.dataset.toggleFollow) {
    runTask(() => toggleFollow(target.dataset.toggleFollow));
    return;
  }

  if (target.dataset.followBack) {
    runTask(() => toggleFollow(target.dataset.followBack));
    return;
  }

  if (target.dataset.setSocialTab) {
    state.socialTab = target.dataset.setSocialTab === "followers" ? "followers" : "following";
    if (state.overlayMode === "following") {
      renderOverlay();
      return;
    }
    renderPage();
    return;
  }

  if (target.dataset.likePost) {
    runTask(() => togglePostLike(target.dataset.likePost));
    return;
  }

  if (target.dataset.favoritePost) {
    runTask(() => togglePostFavorite(target.dataset.favoritePost));
    return;
  }

  if (target.dataset.commentPost) {
    runTask(() => submitPostComment(target.dataset.commentPost));
    return;
  }

  if (target.dataset.openChat) {
    state.chatTargetProfileId = target.dataset.openChat;
    state.chatDraft = "";
    const thread = getThreadForProfile(target.dataset.openChat);
    if (thread?.id) {
      markThreadRead(thread.id);
    }
    openOverlay("chat");
    return;
  }

  if (target.dataset.rateShortcut) {
    if (state.activePage !== "profile") {
      state.profileReturnPage = state.activePage;
    }
    state.activeProfileId = target.dataset.rateShortcut;
    state.activePage = "profile";
    syncNavActive();
    renderPage();
    appView.scrollTop = 0;
    return;
  }

  if (target.dataset.switchManaged) {
    const managedProfile = getProfile(target.dataset.switchManaged);
    if (!managedProfile) return;
    state.activeProfileId = managedProfile.id;
    state.currentActorProfileId = managedProfile.id;
    state.composeProfileId = managedProfile.id;
    runTask(() => selectRole(managedProfile.role));
    return;
  }

  if (target.dataset.editRole) {
    openRegister(target.dataset.editRole);
    return;
  }

  if (target.dataset.rateProfile && target.dataset.rateValue) {
    state.ratingDrafts[target.dataset.rateProfile] = Number(target.dataset.rateValue);
    renderPage();
    return;
  }

  if (target.dataset.submitRating) {
    runTask(() => submitRating(target.dataset.submitRating));
    return;
  }

  if (target.dataset.toggleCommonSport) {
    toggleCommonSportSelection(target.dataset.toggleCommonSport);
    return;
  }

  if (target.dataset.editCommonSports) {
    if (state.workoutSession) return;
    openCheckinEditor();
    return;
  }

  if (target.dataset.cancelCommonSports) {
    cancelCheckinEditor();
    return;
  }

  if (target.dataset.saveCommonSports) {
    runTask(() => saveFavoriteSports());
    return;
  }

  if (target.dataset.selectWorkoutSport) {
    if (state.workoutSession) return;
    runTask(() => selectWorkoutSport(target.dataset.selectWorkoutSport));
    return;
  }

  if (target.dataset.goWorkout) {
    runTask(() => startWorkoutSession());
    return;
  }

  if (target.dataset.startWorkout) {
    runTask(() => startWorkoutSession(target.dataset.startWorkout));
    return;
  }

  if (target.dataset.finishWorkout) {
    runTask(() => finishWorkoutSession());
    return;
  }

  if (target.dataset.retryFinishWorkout) {
    runTask(() => retryFinishedWorkoutSave());
    return;
  }

  if (target.dataset.pauseWorkout) {
    runTask(() => toggleWorkoutPause());
    return;
  }

  if (target.dataset.cancelWorkout) {
    cancelWorkoutSession();
    return;
  }

  if (target.dataset.syncHealthDevice) {
    runTask(() => importHealthDevice(target.dataset.syncHealthDevice));
    renderPage();
    return;
  }

  if (target.dataset.createBooking) {
    const profile = getProfile(target.dataset.createBooking);
    const planIndex = Number(target.dataset.planIndex || 0);
    const plan = profile?.pricingPlans?.[planIndex] || null;
    runTask(() => createBooking(target.dataset.createBooking, plan));
  }
});

appView.addEventListener("input", (event) => {
  if (event.target.dataset.searchInput) {
    state.searchKeyword = event.target.value;
    renderPage();
  }

  if (event.target.dataset.reviewInput) {
    state.reviewDrafts[event.target.dataset.reviewInput] = event.target.value;
  }

  if (event.target.dataset.commentInput) {
    state.commentDrafts[event.target.dataset.commentInput] = event.target.value;
  }
});

overlay.addEventListener("click", (event) => {
  const target = event.target.closest("[data-close-overlay], button, article");
  if (!target) return;

  if (target.dataset.closeOverlay) {
    closeOverlay();
    return;
  }

  if (target.dataset.openProfile) {
    closeOverlay();
    openProfile(target.dataset.openProfile);
    return;
  }

  if (target.dataset.openMediaDetail) {
    openMediaViewer(target.dataset.openMediaDetail, Number(target.dataset.mediaIndex || 0));
    return;
  }

  if (target.dataset.shiftMediaIndex) {
    const entry = getMediaViewerEntry();
    if (!entry) return;
    const nextIndex = Math.min(
      Math.max(0, entry.index + Number(target.dataset.shiftMediaIndex || 0)),
      entry.total - 1
    );
    state.mediaViewerIndex = nextIndex;
    renderOverlay();
    return;
  }

  if (target.dataset.toggleFollow) {
    runTask(() => toggleFollow(target.dataset.toggleFollow));
    return;
  }

  if (target.dataset.followBack) {
    runTask(() => toggleFollow(target.dataset.followBack));
    return;
  }

  if (target.dataset.chooseRole) {
    if (hasManagedRole(target.dataset.chooseRole)) {
      runTask(async () => {
        await selectRole(target.dataset.chooseRole);
        closeOverlay();
      });
      return;
    }
    openRegister(target.dataset.chooseRole);
    return;
  }

  if (target.dataset.openAuth) {
    openAuth(target.dataset.openAuth);
    return;
  }

  if (target.dataset.openRegisterFromAuth) {
    openRegister(target.dataset.openRegisterFromAuth);
    return;
  }

  if (target.dataset.registerRole) {
    state.registerRole = target.dataset.registerRole;
    seedRegisterDraft(state.registerRole);
    state.registerCodeCooldownUntil = 0;
    setRegisterDraftValue(state.registerRole, "verification_code", getRegisterDraft(state.registerRole).verification_code || "");
    state.registerWheelField = "";
    renderOverlay();
    return;
  }

  if (target.dataset.openRegisterWheel) {
    seedRegisterDraft(state.registerRole);
    state.registerWheelField = target.dataset.openRegisterWheel;
    renderOverlay();
    return;
  }

  if (target.dataset.closeRegisterWheel || target.dataset.confirmRegisterWheel) {
    state.registerWheelField = "";
    renderOverlay();
    return;
  }

  if (target.dataset.registerWheelOption) {
    setRegisterDraftValue(state.registerRole, target.dataset.registerWheelOption, target.dataset.wheelValue || "");
    syncRegisterWheelDom(target.dataset.registerWheelOption);
    scrollRegisterWheelToValue(target.dataset.registerWheelOption, "smooth");
    return;
  }

  if (target.dataset.authRole) {
    state.authRole = target.dataset.authRole;
    const remembered = getStoredAccountForRole(state.authRole);
    const hasTypedPhone = Boolean(normalizePhone(state.authPhone));
    if (remembered && !hasTypedPhone && !state.authMatches.length) {
      state.authAccountId = remembered.id;
      state.authRestoreToken = remembered.restoreToken;
      state.authPhone = remembered.phone;
    } else {
      state.authAccountId = "";
      state.authRestoreToken = "";
    }
    state.authMessage = "";
    renderOverlay();
    return;
  }

  if (target.dataset.sendAuthCode) {
    runTask(() => sendAuthVerificationCode());
    return;
  }

  if (target.dataset.sendRegisterCode) {
    runTask(() => sendRegisterVerificationCode());
    return;
  }

  if (target.dataset.authMatchRole) {
    state.authRole = target.dataset.authMatchRole;
    state.authMessage = `已切换到 ${getRoleLabel(state.authRole)}，现在可以直接登录。`;
    renderOverlay();
    return;
  }

  if (target.dataset.quickLoginRole && target.dataset.quickLoginPhone) {
    state.authRole = target.dataset.quickLoginRole;
    state.authPhone = target.dataset.quickLoginPhone;
    state.authAccountId = target.dataset.quickLoginAccountId || "";
    state.authRestoreToken = target.dataset.quickLoginRestoreToken || "";
    renderOverlay();
    return;
  }

  if (target.dataset.composeProfile) {
    state.composeProfileId = target.dataset.composeProfile;
    renderOverlay();
    return;
  }

  if (target.dataset.removeComposeMediaIndex) {
    const index = Number(target.dataset.removeComposeMediaIndex || -1);
    const item = Array.isArray(state.composeMedia) ? state.composeMedia[index] : null;
    if (!item) return;
    state.composeMedia = state.composeMedia.filter((_, itemIndex) => itemIndex !== index);
    renderOverlay();
    runTask(() => deleteManagedMediaItems([item], { silent: true }));
    return;
  }

  if (target.dataset.cityPreset) {
    runTask(() => applyPresetCity(target.dataset.cityPreset));
    return;
  }

  if (target.dataset.applyManualCity) {
    runTask(() => applyManualCity());
    return;
  }

  if (target.dataset.openCity) {
    openCitySelector(state.overlayMode === "register" ? "register" : null);
    return;
  }

  if (target.dataset.action === "locate") {
    requestCurrentLocation();
  }
});

overlay.addEventListener("input", (event) => {
  if (event.target.dataset.cityInput) {
    state.cityInput = event.target.value;
  }

  if (event.target.form?.id === "registerForm" && event.target.name && event.target.type !== "file") {
    setRegisterDraftValue(state.registerRole, event.target.name, event.target.value);
  }

  if (event.target.dataset.authPhone) {
    const nextPhone = event.target.value;
    if (normalizePhone(nextPhone) !== normalizePhone(state.authPhone)) {
      clearAuthResolution();
      state.authCodeCooldownUntil = 0;
      state.authMessage = "";
      if (authLookupTimeout) {
        window.clearTimeout(authLookupTimeout);
        authLookupTimeout = null;
      }
    }
    state.authPhone = nextPhone;
    const normalizedPhone = normalizePhone(nextPhone);
    if (normalizedPhone.length >= 11) {
      authLookupTimeout = window.setTimeout(() => {
        runTask(async () => {
          if (state.overlayMode !== "auth") return;
          if (normalizePhone(state.authPhone) !== normalizedPhone) return;
          await lookupAuthMatches(normalizedPhone);
        });
      }, 220);
    }
  }

  if (event.target.dataset.authCode) {
    state.authVerificationCode = event.target.value;
  }

  if (event.target.dataset.composeContent) {
    state.composeContent = event.target.value;
  }

  if (event.target.dataset.chatInput) {
    state.chatDraft = event.target.value;
    syncChatComposerState();
  }
});

overlay.addEventListener("change", (event) => {
  if (event.target.dataset.composeMediaInput) {
    runTask(async () => {
      const files = Array.from(event.target.files || []).slice(0, 9);
      const existing = Array.isArray(state.composeMedia) ? [...state.composeMedia] : [];
      const nextMedia = await readMediaFiles(files);
      const combined = [...existing];
      nextMedia.forEach((item) => {
        const alreadyExists = combined.some(
          (current) => current.type === item.type && current.name === item.name && current.url === item.url
        );
        if (!alreadyExists && combined.length < 9) {
          combined.push(item);
        }
      });
      state.composeMedia = combined;
      event.target.value = "";
      renderOverlay();
    });
    return;
  }

  if (event.target.form?.id === "registerForm" && event.target.name && event.target.type !== "file") {
    setRegisterDraftValue(state.registerRole, event.target.name, event.target.value);
  }

  if (event.target.type === "file" && event.target.name) {
    runTask(async () => {
      const files = Array.from(event.target.files || []);
      if (!files.length) {
        delete state.registerUploadDrafts[event.target.name];
        renderOverlay();
        return;
      }
      state.registerUploadDrafts[event.target.name] = {
        label: files.length === 1 ? files[0].name : `已选择 ${files.length} 个文件`,
        preview: files[0].type.startsWith("image/")
          ? await optimizeImageFile(files[0], { maxEdge: 240, quality: 0.74 })
          : ""
      };
      renderOverlay();
    });
  }
});

overlay.addEventListener("submit", (event) => {
  if (event.target.id === "authForm") {
    event.preventDefault();
    runTask(() => submitAuthLogin());
    return;
  }

  if (event.target.id === "registerForm") {
    event.preventDefault();
    const formData = new FormData(event.target);
    runTask(() => upsertManagedProfile(state.registerRole, formData));
    return;
  }

  if (event.target.id === "composeForm") {
    event.preventDefault();
    runTask(() => submitComposePost());
    return;
  }

  if (event.target.id === "chatForm") {
    event.preventDefault();
    runTask(() => sendDirectMessage(state.chatTargetProfileId));
    return;
  }
});

navLinks.forEach((link) => {
  link.addEventListener("click", () => {
    closeOverlay();
    state.overlayReturnMode = null;
    state.registerWheelField = "";
    state.chatTargetProfileId = "";
    state.authMessage = "";
    if (link.dataset.page === "profile") {
      openMyPage();
      return;
    }
    state.profileSubpage = "";
    state.outdoorShareCheckinId = "";
    state.activePage = link.dataset.page;
    syncNavActive();
    renderPage();
    appView.scrollTop = 0;
  });
});

fabButton.addEventListener("click", openComposer);

function beginProfileSwipe(clientX, clientY, sourceTarget, pointerId = null) {
  if (state.activePage !== "profile" || state.overlayMode) return false;
  const activeProfile = getProfile(state.activeProfileId) || getMyPageProfile();
  const myProfile = getMyPageProfile();
  if (
    !state.profileSubpage &&
    activeProfile?.id &&
    myProfile?.id &&
    activeProfile.id === myProfile.id &&
    activeProfile.role === "enthusiast"
  ) {
    return false;
  }
  const bounds = appView.getBoundingClientRect();
  const localX = clientX - bounds.left;
  if (localX > 56) return false;
  if (sourceTarget instanceof Element && sourceTarget.closest("button, input, textarea, select, video")) {
    return false;
  }

  profileSwipe.active = true;
  profileSwipe.engaged = false;
  profileSwipe.pointerId = pointerId;
  profileSwipe.startX = clientX;
  profileSwipe.startY = clientY;
  profileSwipe.offset = 0;
  return true;
}

appView.addEventListener("pointerdown", (event) => {
  if (event.pointerType === "touch") return;
  if (event.pointerType === "mouse" && event.button !== 0) return;
  if (!beginProfileSwipe(event.clientX, event.clientY, event.target, event.pointerId)) return;
  if (typeof appView.setPointerCapture === "function") {
    try {
      appView.setPointerCapture(event.pointerId);
    } catch (_error) {
      // Ignore unsupported capture behavior in some browsers.
    }
  }
});

appView.addEventListener("pointermove", (event) => {
  if (!profileSwipe.active || event.pointerId !== profileSwipe.pointerId) return;

  const deltaX = event.clientX - profileSwipe.startX;
  const deltaY = event.clientY - profileSwipe.startY;

  if (!profileSwipe.engaged) {
    if (deltaX <= 0 || Math.abs(deltaY) > Math.abs(deltaX)) {
      if (Math.abs(deltaY) > 18) resetProfileSwipe();
      return;
    }

    if (deltaX < 14) return;
    profileSwipe.engaged = true;
    appView.classList.add("is-swipe-preview");
  }

  event.preventDefault();
  profileSwipe.offset = Math.max(0, Math.min(deltaX, 118));
  appView.style.transition = "none";
  appView.style.transform = `translateX(${profileSwipe.offset}px)`;
});

appView.addEventListener(
  "touchstart",
  (event) => {
    const touch = event.changedTouches[0];
    if (!touch) return;
    beginProfileSwipe(touch.clientX, touch.clientY, event.target);
  },
  { passive: true }
);

appView.addEventListener(
  "touchmove",
  (event) => {
    if (!profileSwipe.active) return;
    const touch = event.changedTouches[0];
    if (!touch) return;

    const deltaX = touch.clientX - profileSwipe.startX;
    const deltaY = touch.clientY - profileSwipe.startY;

    if (!profileSwipe.engaged) {
      if (deltaX <= 0 || Math.abs(deltaY) > Math.abs(deltaX)) {
        if (Math.abs(deltaY) > 18) resetProfileSwipe();
        return;
      }

      if (deltaX < 14) return;
      profileSwipe.engaged = true;
      appView.classList.add("is-swipe-preview");
    }

    event.preventDefault();
    profileSwipe.offset = Math.max(0, Math.min(deltaX, 118));
    appView.style.transition = "none";
    appView.style.transform = `translateX(${profileSwipe.offset}px)`;
  },
  { passive: false }
);

function finishProfileSwipe(shouldNavigate) {
  if (!profileSwipe.active) return;

  const pointerId = profileSwipe.pointerId;
  profileSwipe.active = false;
  profileSwipe.pointerId = null;

  if (typeof appView.releasePointerCapture === "function" && pointerId !== null) {
    try {
      appView.releasePointerCapture(pointerId);
    } catch (_error) {
      // Ignore unsupported capture behavior in some browsers.
    }
  }

  if (!profileSwipe.engaged) {
    resetProfileSwipe();
    return;
  }

  if (shouldNavigate) {
    appView.classList.add("is-swipe-preview");
    appView.style.transition = "transform 140ms ease";
    appView.style.transform = "translateX(124px)";
    window.setTimeout(() => {
      goBackFromProfile();
    }, 120);
    return;
  }

  appView.style.transition = "transform 180ms ease";
  appView.style.transform = "";
  window.setTimeout(() => {
    resetProfileSwipe();
  }, 180);
}

appView.addEventListener("pointerup", (event) => {
  if (event.pointerId !== profileSwipe.pointerId) return;
  finishProfileSwipe(profileSwipe.offset > 84);
});

appView.addEventListener("pointercancel", (event) => {
  if (event.pointerId !== profileSwipe.pointerId) return;
  finishProfileSwipe(false);
});

appView.addEventListener("touchend", () => {
  if (!profileSwipe.active) return;
  finishProfileSwipe(profileSwipe.offset > 72);
});

appView.addEventListener("touchcancel", () => {
  if (!profileSwipe.active) return;
  finishProfileSwipe(false);
});

function syncViewportHeight() {
  document.documentElement.style.setProperty("--app-vh", `${window.innerHeight}px`);
}

function registerAppServiceWorker() {
  if (!("serviceWorker" in navigator)) return;
  const swUrl = `${URL_PREFIX || ""}/sw.js?v=20260424-5`;
  window.addEventListener("load", () => {
    navigator.serviceWorker
      .register(swUrl, { updateViaCache: "none" })
      .then((registration) => registration.update().catch(() => {}))
      .catch(() => {});
  });
}

syncViewportHeight();
registerAppServiceWorker();
window.addEventListener("resize", syncViewportHeight, { passive: true });
window.addEventListener("orientationchange", syncViewportHeight, { passive: true });
window.__FITHUB_READY__ = false;
window.__FITHUB_BOOTSTRAP_DONE__ = false;

const cachedSnapshot = getStoredSnapshot();
if (cachedSnapshot?.session) {
  syncStateFromServer(cachedSnapshot, { keepOverlay: true });
  state.isBootstrapping = false;
}

if (!state.managedProfileIds.length) {
  bootstrapRememberedAccountLocally();
}

renderPage();
window.__FITHUB_READY__ = true;
refreshSharedState().catch((error) => {
  state.isBootstrapping = false;
  renderPage();
  window.__FITHUB_READY__ = true;
  window.__FITHUB_BOOTSTRAP_DONE__ = true;
  showError(error?.message || "试用服务连接失败，请稍后刷新页面。");
});
window.addEventListener("visibilitychange", () => {
  if (document.hidden) return;
  if (Date.now() - lastSuccessfulSyncAt < 10000) return;
  refreshSharedState({ keepOverlay: true }).catch(() => {});
});
window.setInterval(() => {
  if (document.hidden) return;
  if (state.overlayMode === "register" || state.overlayMode === "compose" || state.overlayMode === "chat") return;
  refreshSharedState({ keepOverlay: true }).catch(() => {});
}, 45000);
window.setInterval(() => {
  if (document.hidden) return;
  if (!state.workoutSession) return;
  if (state.activePage !== "profile") return;
  if (state.overlayMode) return;
  renderPage();
}, 1000);
