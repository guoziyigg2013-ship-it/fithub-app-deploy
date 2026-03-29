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
  { id: "run", label: "跑步", hint: "户外 / 跑步机", icon: "跑" },
  { id: "strength", label: "传统力量训练", hint: "器械 / 自由重量", icon: "力" },
  { id: "cycling", label: "骑行", hint: "动感单车 / 户外", icon: "骑" },
  { id: "hiit", label: "HIIT", hint: "燃脂间歇", icon: "燃" },
  { id: "pilates", label: "普拉提", hint: "核心稳定", icon: "普" },
  { id: "swim", label: "游泳", hint: "有氧耐力", icon: "泳" },
  { id: "yoga", label: "瑜伽拉伸", hint: "恢复舒展", icon: "伸" },
  { id: "basketball", label: "球类运动", hint: "篮球 / 羽毛球", icon: "球" }
];

const CHECKIN_SPORT_METRICS = {
  run: { met: 8.3, paceKmh: 8.5 },
  strength: { met: 6.0, paceKmh: 0 },
  cycling: { met: 7.2, paceKmh: 18 },
  hiit: { met: 8.8, paceKmh: 0 },
  pilates: { met: 3.0, paceKmh: 0 },
  swim: { met: 6.0, paceKmh: 2.1 },
  yoga: { met: 2.8, paceKmh: 0 },
  basketball: { met: 7.5, paceKmh: 4.2 }
};

function createDemoImage(title, accentA, accentB) {
  const svg = `
    <svg xmlns="http://www.w3.org/2000/svg" width="800" height="520" viewBox="0 0 800 520">
      <defs>
        <linearGradient id="g" x1="0" x2="1" y1="0" y2="1">
          <stop offset="0%" stop-color="${accentA}"/>
          <stop offset="100%" stop-color="${accentB}"/>
        </linearGradient>
      </defs>
      <rect width="800" height="520" rx="36" fill="url(#g)"/>
      <circle cx="664" cy="132" r="92" fill="rgba(255,255,255,0.16)"/>
      <circle cx="152" cy="392" r="116" fill="rgba(255,255,255,0.14)"/>
      <text x="60" y="246" fill="white" font-size="56" font-family="Arial, PingFang SC, sans-serif" font-weight="700">${title}</text>
      <text x="60" y="306" fill="rgba(255,255,255,0.88)" font-size="28" font-family="Arial, PingFang SC, sans-serif">FitHub Moments Demo</text>
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
      <ellipse cx="248" cy="78" rx="52" ry="36" fill="rgba(255,255,255,0.18)"/>
      <ellipse cx="74" cy="256" rx="96" ry="62" fill="rgba(255,255,255,0.1)"/>
      <circle cx="160" cy="116" r="58" fill="${skin}"/>
      <path d="M101 120c2-42 28-66 59-66 35 0 61 22 63 65-18-18-44-26-62-26-23 0-41 7-60 27z" fill="${hair}"/>
      <rect x="112" y="161" width="96" height="46" rx="20" fill="${skin}"/>
      <path d="M74 304c8-55 42-87 86-87 44 0 78 32 86 87z" fill="url(#shirt)"/>
      <circle cx="140" cy="119" r="4" fill="#38251c"/>
      <circle cx="180" cy="119" r="4" fill="#38251c"/>
      <path d="M143 146c8 8 26 8 34 0" fill="none" stroke="#bc7a63" stroke-width="5" stroke-linecap="round"/>
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
      </defs>
      <rect width="320" height="320" rx="52" fill="url(#bg)"/>
      <rect x="54" y="66" width="212" height="170" rx="22" fill="rgba(18,22,28,0.68)"/>
      <rect x="72" y="86" width="58" height="20" rx="10" fill="${accent}"/>
      <rect x="78" y="138" width="18" height="64" rx="8" fill="#d9dee7"/>
      <rect x="112" y="126" width="18" height="76" rx="8" fill="#d9dee7"/>
      <rect x="154" y="118" width="18" height="84" rx="8" fill="#d9dee7"/>
      <rect x="190" y="132" width="18" height="70" rx="8" fill="#d9dee7"/>
      <rect x="226" y="144" width="18" height="58" rx="8" fill="#d9dee7"/>
      <rect x="64" y="248" width="192" height="24" rx="12" fill="rgba(255,255,255,0.14)"/>
      <path d="M74 214h172" stroke="rgba(255,255,255,0.2)" stroke-width="6" stroke-linecap="round"/>
    </svg>
  `;
  return `data:image/svg+xml;charset=UTF-8,${encodeURIComponent(svg)}`;
}

const DEMO_PROFILE_PATCHES = {
  "gym-demo-a": {
    name: "模拟健身房 A · 万象燃炼馆",
    avatar: "万",
    avatarImage:
      "https://images.pexels.com/photos/6046979/pexels-photo-6046979.png?auto=compress&cs=tinysrgb&fit=crop&w=160&h=160&dpr=1",
    coverImage:
      "https://images.pexels.com/photos/6046979/pexels-photo-6046979.png?auto=compress&cs=tinysrgb&fit=crop&w=640&h=360&dpr=1",
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
    avatarImage:
      "https://images.pexels.com/photos/35215412/pexels-photo-35215412.jpeg?auto=compress&cs=tinysrgb&fit=crop&w=160&h=160&dpr=1",
    coverImage:
      "https://images.pexels.com/photos/35215412/pexels-photo-35215412.jpeg?auto=compress&cs=tinysrgb&fit=crop&w=640&h=360&dpr=1",
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
    avatarImage:
      "https://images.pexels.com/photos/28455437/pexels-photo-28455437.jpeg?auto=compress&cs=tinysrgb&fit=crop&w=180&h=180&dpr=1",
    coverImage:
      "https://images.pexels.com/photos/28455437/pexels-photo-28455437.jpeg?auto=compress&cs=tinysrgb&fit=crop&w=640&h=360&dpr=1",
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
    avatarImage:
      "https://images.pexels.com/photos/14055666/pexels-photo-14055666.jpeg?auto=compress&cs=tinysrgb&fit=crop&w=180&h=180&dpr=1",
    coverImage:
      "https://images.pexels.com/photos/14055666/pexels-photo-14055666.jpeg?auto=compress&cs=tinysrgb&fit=crop&w=640&h=360&dpr=1",
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

function applyDemoProfilePatch(profile) {
  if (!profile) return profile;
  const patch = DEMO_PROFILE_PATCHES[profile.id];
  if (!patch) return profile;
  return {
    ...profile,
    ...patch
  };
}

function enhanceProfiles(profiles = []) {
  return profiles.map((profile) => applyDemoProfilePatch(profile));
}

function createSupplementalDemoProfiles() {
  return enhanceProfiles([
    {
      id: "gym-demo-c",
      role: "gym",
      name: "模拟健身房 C · Skyline Strength",
      handle: "@demo.gym.c",
      avatar: "天",
      avatarImage:
        "https://images.pexels.com/photos/29149075/pexels-photo-29149075.jpeg?auto=compress&cs=tinysrgb&fit=crop&w=160&h=160&dpr=1",
      coverImage:
        "https://images.pexels.com/photos/29149075/pexels-photo-29149075.jpeg?auto=compress&cs=tinysrgb&fit=crop&w=640&h=360&dpr=1",
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
              url: "https://images.pexels.com/photos/29149075/pexels-photo-29149075.jpeg?auto=compress&cs=tinysrgb&fit=crop&w=640&h=640&dpr=1",
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
      avatarImage:
        "https://images.pexels.com/photos/4716817/pexels-photo-4716817.jpeg?auto=compress&cs=tinysrgb&fit=crop&w=160&h=160&dpr=1",
      coverImage:
        "https://images.pexels.com/photos/4716817/pexels-photo-4716817.jpeg?auto=compress&cs=tinysrgb&fit=crop&w=640&h=360&dpr=1",
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
              url: "https://images.pexels.com/photos/4716817/pexels-photo-4716817.jpeg?auto=compress&cs=tinysrgb&fit=crop&w=640&h=640&dpr=1",
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
      avatarImage:
        "https://images.pexels.com/photos/11327778/pexels-photo-11327778.jpeg?auto=compress&cs=tinysrgb&fit=crop&w=180&h=180&dpr=1",
      coverImage:
        "https://images.pexels.com/photos/11327778/pexels-photo-11327778.jpeg?auto=compress&cs=tinysrgb&fit=crop&w=640&h=360&dpr=1",
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
          meta: "模拟动态 · 训练营上新"
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
      avatarImage:
        "https://images.pexels.com/photos/20418608/pexels-photo-20418608.jpeg?auto=compress&cs=tinysrgb&fit=crop&w=180&h=180&dpr=1",
      coverImage:
        "https://images.pexels.com/photos/20418608/pexels-photo-20418608.jpeg?auto=compress&cs=tinysrgb&fit=crop&w=640&h=360&dpr=1",
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
          meta: "模拟动态 · 晚间时段"
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

    const presets = {
      avatar: { w: "160", h: "160" },
      cover: { w: "640", h: "360" },
      feed: { w: "720", h: "720" }
    };
    const preset = presets[kind] || presets.avatar;

    remoteUrl.searchParams.set("auto", "compress");
    remoteUrl.searchParams.set("cs", "tinysrgb");
    remoteUrl.searchParams.set("fit", "crop");
    remoteUrl.searchParams.set("dpr", "1");
    remoteUrl.searchParams.set("w", preset.w);
    remoteUrl.searchParams.set("h", preset.h);
    return remoteUrl.toString();
  } catch (_error) {
    return url;
  }
}

function hydrateAsyncImages(root = document) {
  root.querySelectorAll(".image-shell").forEach((shell) => {
    const image = shell.querySelector("img");
    if (!image || shell.dataset.imageHydrated === "1") return;
    shell.dataset.imageHydrated = "1";

    const markLoaded = () => {
      shell.classList.remove("is-failed");
      shell.classList.add("is-loaded");
    };

    const markFailed = () => {
      shell.classList.remove("is-loaded");
      shell.classList.add("is-failed");
    };

    if (image.complete && image.naturalWidth > 0) {
      markLoaded();
      return;
    }

    if (image.complete && !image.naturalWidth) {
      markFailed();
      return;
    }

    image.addEventListener("load", markLoaded, { once: true });
    image.addEventListener("error", markFailed, { once: true });
  });
}

function createDefaultAvatar(role, name) {
  if (role === "gym") {
    return createGymAvatar({ bgA: "#293744", bgB: "#7a97af", accent: "#f28c28" });
  }

  const palettes = {
    enthusiast: { skin: "#f4ccb2", hair: "#674632", shirt: "#f28c28", bgA: "#f7e0c6", bgB: "#d8a06f" },
    coach: { skin: "#efc1a1", hair: "#2f241d", shirt: "#1f2125", bgA: "#dfe5ef", bgB: "#8d9bb3" }
  };
  return createPortraitAvatar(palettes[role] || palettes.enthusiast);
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
const API_BASE = `${URL_PREFIX}/api`;

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
  cityInput: "",
  profiles: createInitialProfiles(),
  managedProfileIds: [],
  currentActorProfileId: "",
  activeProfileId: "",
  followSet: new Set(),
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
  bookings: bookingCards,
  threads: [],
  checkinEditing: false,
  checkinSelectionDraft: [],
  workoutSession: null,
  chatTargetProfileId: "",
  chatDraft: "",
  sessionId: "",
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
let lastSuccessfulSyncAt = 0;

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
    window.localStorage.setItem(SNAPSHOT_STORAGE_KEY, JSON.stringify(payload));
  } catch (_error) {
    // Ignore storage quota failures.
  }
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
  storeSnapshot(payload);

  state.sessionId = payload.session.id || state.sessionId;
  storeSessionId(state.sessionId);
  state.selectedRole = payload.session.selectedRole || state.selectedRole;
  state.registerRole = payload.session.selectedRole || state.registerRole;
  state.userPosition = payload.session.userPosition || state.userPosition;
  state.locationStatus = payload.session.locationStatus || state.locationStatus;
  state.profiles = enhanceProfiles(payload.profiles || []);
  state.managedProfileIds = payload.session.managedProfileIds || [];
  state.currentActorProfileId = payload.session.currentActorProfileId || state.managedProfileIds[0] || "";
  state.followSet = new Set(payload.followSet || []);
  state.bookings = payload.bookings || [];
  state.threads = payload.threads || [];
  state.composeProfileId = state.composeProfileId || state.currentActorProfileId || state.managedProfileIds[0] || "";

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
}

async function refreshSharedState({ keepOverlay = false } = {}) {
  if (refreshPromise) return refreshPromise;
  const query = state.sessionId || getStoredSessionId();
  const suffix = query ? `?session_id=${encodeURIComponent(query)}` : "";
  refreshPromise = apiRequest(`${API_BASE}/bootstrap${suffix}`)
    .then((payload) => {
      syncStateFromServer(payload, { keepOverlay });
      state.isBootstrapping = false;
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
  const payload = await apiRequest(path, {
    method: "POST",
    body: {
      sessionId: state.sessionId || getStoredSessionId(),
      ...body
    }
  });
  syncStateFromServer(payload, { keepOverlay });
  state.isBootstrapping = false;
  return payload;
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

async function readSingleFile(inputName, formData) {
  const draftPreview = state.registerUploadDrafts?.[inputName]?.preview;
  if (draftPreview) return draftPreview;
  const value = formData.get(inputName);
  if (!isProvidedFile(value) || !value.size) return "";
  return optimizeImageFile(value, { maxEdge: 360, quality: 0.72 });
}

async function readMediaFiles(files) {
  const media = [];
  for (const file of files) {
    if (!isProvidedFile(file) || !file.size) continue;
    const url = file.type.startsWith("image/")
      ? await optimizeImageFile(file, { maxEdge: 1080, quality: 0.8 })
      : await readFileAsDataUrl(file);
    media.push({
      type: file.type.startsWith("video/") ? "video" : "image",
      url,
      name: file.name
    });
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
  const avatarText = escapeHtml(profile?.avatar || getInitialCharacter(profile?.name || "?"));
  const avatarAlt = escapeHtml(`${profile?.name || "用户"}头像`);

  if (profile?.avatarImage) {
    return `
      <div class="${safeClassName} avatar--photo image-shell image-shell--avatar">
        <img class="avatar-image" src="${optimizeRemoteImageUrl(profile.avatarImage, "avatar")}" alt="${avatarAlt}" loading="lazy" decoding="async">
      </div>
    `;
  }

  return `<div class="${safeClassName}">${avatarText}</div>`;
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
  return state.profiles
    .filter(
      (profile) =>
        profile.id !== actor?.id &&
        profile.listed &&
        !state.followSet.has(profile.id)
    )
    .map((profile) => ({
      ...profile,
      sameCity: profile.city === state.userPosition.city ? 1 : 0
    }))
    .sort((left, right) => {
      if (right.sameCity !== left.sameCity) return right.sameCity - left.sameCity;
      if (right.ratingAvg !== left.ratingAvg) return right.ratingAvg - left.ratingAvg;
      return right.followers - left.followers;
    })
    .slice(0, 8);
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

function getFollowingFeedItems() {
  const actor = getCurrentActor();
  return state.profiles
    .filter(
      (profile) =>
        profile.listed &&
        profile.id !== actor?.id &&
        state.followSet.has(profile.id)
    )
    .flatMap((profile) =>
      (profile.posts || []).map((post, index) => ({
        id: `${profile.id}-post-${index}`,
        profile,
        post,
        minutes: getRelativeMinutes(post.time)
      }))
    )
    .sort((left, right) => {
      if (left.minutes !== right.minutes) return left.minutes - right.minutes;
      return right.profile.followers - left.profile.followers;
    })
    .slice(0, 10);
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
  if (state.overlayMode === "register") {
    state.registerUploadDrafts = {};
  }
  state.overlayMode = null;
  state.registerSuccess = "";
  renderOverlay();
}

function openRegister(role = state.selectedRole) {
  state.registerRole = role;
  state.selectedRole = role;
  state.overlayReturnMode = null;
  state.registerUploadDrafts = {};
  openOverlay("register");
}

function openMyPage() {
  const myProfile = getMyPageProfile();
  if (state.activePage !== "profile") {
    state.profileReturnPage = state.activePage;
  }
  state.activePage = "profile";
  state.activeProfileId = myProfile?.id || state.currentActorProfileId || "";
  state.profileSubpage = "";
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

function renderField(field, seed) {
  const value = getFieldDefault(field, seed);

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
    profile: profilePayload
  });
  state.activeProfileId = state.currentActorProfileId;
  state.composeProfileId = state.currentActorProfileId;
  state.selectedRole = role;
  state.activePage = "home";
  state.locationStatus = `${getRoleLabel(role)}注册成功，现在这个设备会记住你的身份，并和其他测试用户共享互动数据。`;
  syncNavActive();
  closeOverlay();
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
    media: state.composeMedia.map((item) => ({
      type: item.type,
      url: item.url,
      name: item.name
    }))
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
  renderPage();
}

function startWorkoutSession(sportId) {
  const profile = getMyPageProfile();
  if (!profile || profile.role !== "enthusiast") {
    throw new Error("请先用健身爱好者身份注册后再开始运动。");
  }
  if (!profile.gender || !getProfileHeight(profile) || !getProfileWeight(profile)) {
    state.profileSubpage = "health";
    renderPage();
    throw new Error("请先完善性别、身高和体重，再开始运动。");
  }

  state.workoutSession = {
    sportId,
    startedAt: Date.now()
  };
  renderPage();
}

function cancelWorkoutSession() {
  state.workoutSession = null;
  renderPage();
}

async function finishWorkoutSession() {
  const profile = getMyPageProfile();
  const session = getWorkoutSessionStats(profile);
  if (!profile || !session) return;

  await postAndSync(`${API_BASE}/checkin/create`, {
    profileId: profile.id,
    sportId: session.sport.id,
    sportLabel: session.sport.label,
    duration: session.elapsedMinutes,
    calories: session.calories,
    distance: session.distance,
    note: "",
    content: `完成了一次 ${session.sport.label} 训练，持续 ${session.elapsedMinutes} 分钟，估算消耗 ${session.calories} kcal。`
  });

  state.workoutSession = null;
  renderPage();
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
  await postAndSync(`${API_BASE}/post/like`, { postId }, { keepOverlay: Boolean(state.overlayMode) });
  renderPage();
}

async function submitPostComment(postId) {
  const text = (state.commentDrafts[postId] || "").trim();
  if (!text) return;
  await postAndSync(`${API_BASE}/post/comment`, { postId, text }, { keepOverlay: Boolean(state.overlayMode) });
  state.commentDrafts[postId] = "";
  renderPage();
}

async function sendDirectMessage(profileId) {
  const text = state.chatDraft.trim();
  if (!text) return;
  await postAndSync(`${API_BASE}/message/send`, {
    targetProfileId: profileId,
    text
  }, { keepOverlay: true });
  state.chatDraft = "";
  state.overlayMode = "chat";
  renderOverlay();
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
                (profile) => `
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
                        <button class="cta" type="button" data-open-profile="${profile.id}">主页</button>
                      </div>
                    </div>
                  </article>
                `
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
  const managedProfile = getCurrentActor();

  appView.innerHTML = `
    <section class="page-header">
      <div>
        <p class="page-label">Discover</p>
        <h1>探索</h1>
      </div>
      <button class="mini-button mini-button--accent" data-open-following="1" type="button">我关注的</button>
    </section>

    <section class="section-title-row section-title-row--discover-recommended">
      <div>
        <h3>推荐关注</h3>
        <p class="result-tip">优先推荐附近的健身房、教练和健身搭子</p>
      </div>
      <button class="text-link" data-open-profile="${managedProfile?.id || ""}" type="button">我的主页</button>
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
              .map(({ profile, post }) => renderPostCard(profile, post, { compact: true }))
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
  const bookingList = state.bookings || [];
  const bookingDashboard = myProfile ? getBookingDashboard(myProfile) : { pendingCount: 0, weeklyCheckins: 0, points: 0 };
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
        <span>本周待上课</span>
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
      ${bookingList.length
        ? bookingList
            .map(
              (card) => `
                <article class="booking-card">
                  <div class="booking-top">
                    <strong>${escapeHtml(card.title)}</strong>
                    <span class="status-pill">${escapeHtml(card.status)}</span>
                  </div>
                  <p>${escapeHtml(card.place)}</p>
                  <div class="community-meta">
                    <span>${escapeHtml(card.price || "待确认")}</span>
                    <span>${escapeHtml(card.time)}</span>
                  </div>
                  <div class="booking-bottom">
                    <span>支持查看订单详情、跳转主页和后续评分。</span>
                    <button class="cta" type="button" data-open-profile="${card.profileId || card.targetProfileId || ""}">${escapeHtml(card.action)}</button>
                  </div>
                </article>
              `
            )
            .join("")
        : '<article class="empty-card">你还没有正式预约。去首页、探索或教练/场馆主页选择价格方案后，这里才会出现排期和订单。</article>'}
    </section>

    <article class="helper-card">
      <strong>预约说明</strong>
      <p>教练与健身房的定价会同步展示在首页卡片、主页定价模块和探索流里；完成正式预约后，本页才会出现待上课与订单内容。</p>
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
        .map((item) => {
          if (item.type === "video") {
            return `
              <div class="timeline-media-card image-shell image-shell--cover is-loaded">
                <video class="timeline-media-video" src="${item.url}" controls playsinline preload="metadata"></video>
              </div>
            `;
          }

          return `
            <div class="timeline-media-card image-shell image-shell--cover">
              <img class="timeline-media-image" src="${optimizeRemoteImageUrl(item.url, "feed")}" alt="${escapeHtml(item.name || "动态图片")}" loading="lazy" decoding="async">
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

function renderPostCard(profile, post, options = {}) {
  const { compact = false, showProfileButton = true } = options;
  const commentDraft = state.commentDrafts[post.id] || "";
  const showChatButton = canOpenChatWith(profile.id);
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
    <article class="timeline-card ${compact ? "timeline-card--compact" : ""}">
      <div class="timeline-head">
        <div class="timeline-author">
          ${renderAvatarMarkup(profile, "avatar")}
          <div>
            <strong>${escapeHtml(profile.name)}</strong>
            <p>${escapeHtml(profile.handle)} · ${escapeHtml(post.time)}</p>
          </div>
        </div>
        <span>${escapeHtml(getRoleLabel(profile.role))}</span>
      </div>
      <p>${escapeHtml(post.content)}</p>
      ${checkinMeta}
      ${renderPostMedia(post)}
      <small>${escapeHtml(post.meta)}</small>
      <div class="post-action-bar">
        <button class="mini-button ${post.likedByCurrentActor ? "mini-button--accent" : ""}" data-like-post="${post.id}" type="button">
          ${post.likedByCurrentActor ? "已赞" : "点赞"} ${post.likeCount ? `(${post.likeCount})` : ""}
        </button>
        <span class="post-action-count">评论 ${post.comments?.length || 0}</span>
        ${
          showProfileButton
            ? `<button class="mini-button" data-open-profile="${profile.id}" type="button">查看主页</button>`
            : ""
        }
        ${
          showChatButton
            ? `<button class="mini-button" data-open-chat="${profile.id}" type="button">私信</button>`
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

function getCheckinSport(optionId) {
  return CHECKIN_SPORTS.find((item) => item.id === optionId) || CHECKIN_SPORTS[0];
}

function getCheckinMetrics(optionId) {
  return CHECKIN_SPORT_METRICS[optionId] || CHECKIN_SPORT_METRICS.strength;
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

function getProfileWeight(profile) {
  return Number(profile?.weightKg || 0);
}

function getProfileHeight(profile) {
  return Number(profile?.heightCm || 0);
}

function getProfileBMI(profile) {
  const heightCm = getProfileHeight(profile);
  const weightKg = getProfileWeight(profile);
  if (!heightCm || !weightKg) return "--";
  const heightMeter = heightCm / 100;
  return (weightKg / (heightMeter * heightMeter)).toFixed(1);
}

function getWorkoutSessionStats(profile) {
  const session = state.workoutSession;
  if (!session) return null;

  const sport = getCheckinSport(session.sportId);
  const metrics = getCheckinMetrics(session.sportId);
  const elapsedSeconds = Math.max(0, Math.floor((Date.now() - session.startedAt) / 1000));
  const elapsedMinutes = Math.max(1, Math.floor(elapsedSeconds / 60));
  const hours = elapsedSeconds / 3600;
  const weightKg = getProfileWeight(profile) || 60;
  const genderFactor = profile?.gender === "女" ? 0.92 : profile?.gender === "男" ? 1.02 : 1;
  const calories = Math.max(1, Math.round((metrics.met * 3.5 * weightKg * hours) / 200 * genderFactor));
  const distance = metrics.paceKmh ? Number((metrics.paceKmh * hours).toFixed(hours >= 1 ? 1 : 2)) : 0;

  return {
    ...session,
    sport,
    elapsedSeconds,
    elapsedMinutes,
    timerLabel: formatWorkoutTimer(elapsedSeconds),
    calories,
    distance
  };
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
  const bookings = state.bookings || [];
  return {
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
      <span>${escapeHtml(sublabel)}</span>
    </button>
  `;
}

function getFavoriteSports(profile) {
  const favoriteIds = profile?.favoriteSports || [];
  return CHECKIN_SPORTS.filter((item) => favoriteIds.includes(item.id));
}

function renderCheckinEntry(profile) {
  const activeSession = getWorkoutSessionStats(profile);
  const weeklyCount = getWeeklyCheckins(profile).length;
  const favoriteSports = getFavoriteSports(profile);

  return `
    <article class="dashboard-checkin">
      <div class="dashboard-checkin-copy">
        <span class="dashboard-checkin-kicker">本周已打卡 ${weeklyCount} 次</span>
        <h3>${activeSession ? `${activeSession.sport.label} 进行中` : "像 Apple Watch 一样开始一次运动"}</h3>
        <p>${activeSession ? `系统正在自动计时，并根据你的身体数据估算卡路里。` : "先选择常规运动项目，之后“打卡”页只显示这些项目，点一下就能开始运动。"}</p>
        <div class="dashboard-checkin-pills">
          ${
            activeSession
              ? `
                <span>${escapeHtml(activeSession.timerLabel)}</span>
                <span>${escapeHtml(`${activeSession.calories} kcal`)}</span>
                ${activeSession.distance ? `<span>${escapeHtml(`${activeSession.distance} km`)}</span>` : ""}
              `
              : favoriteSports.length
                ? favoriteSports.slice(0, 3).map((item) => `<span>${escapeHtml(item.label)}</span>`).join("")
                : "<span>先设置常规项目</span>"
          }
        </div>
      </div>
      <button class="mini-button mini-button--accent" data-open-my-feature="checkin" type="button">${activeSession ? "继续" : "去打卡"}</button>
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
                      <button class="text-link" data-open-profile="${profile.id}" type="button">查看</button>
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

function renderFavoriteSportEditor(profile) {
  const selectedIds = state.checkinSelectionDraft.length
    ? state.checkinSelectionDraft
    : [...(profile.favoriteSports || [])];
  const canSave = selectedIds.length > 0;

  return `
    <article class="detail-card checkin-feature-card">
      <div class="section-title-row">
        <div>
          <h3>选择常规项目</h3>
          <p class="result-tip">先像 Apple Watch 一样，把你最常用的运动项目固定下来，之后打卡页只显示这些项目。</p>
        </div>
        <span class="status-pill">${selectedIds.length} 项</span>
      </div>

      <section class="checkin-sport-grid">
        ${CHECKIN_SPORTS.map(
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
        ).join("")}
      </section>

      <div class="action-row action-row--checkin">
        <button class="mini-button" data-cancel-common-sports="1" type="button">稍后再设</button>
        <button class="primary-submit" ${canSave ? "" : "disabled"} data-save-common-sports="1" type="button">保存常规项目</button>
      </div>
    </article>
  `;
}

function renderWorkoutLauncher(profile) {
  const favoriteSports = getFavoriteSports(profile);

  if (!favoriteSports.length || state.checkinEditing) {
    return renderFavoriteSportEditor(profile);
  }

  return `
    <article class="detail-card checkin-feature-card">
      <div class="section-title-row">
        <div>
          <h3>开始运动</h3>
          <p class="result-tip">轻点项目就会自动开始计时，并按你的性别、身高、体重估算卡路里。</p>
        </div>
        <button class="text-link" data-edit-common-sports="1" type="button">编辑常规项目</button>
      </div>

      <section class="workout-launcher-list">
        ${favoriteSports
          .map(
            (item) => `
              <button class="workout-launcher-row" data-start-workout="${item.id}" type="button">
                <div class="workout-launcher-main">
                  <span class="checkin-sport-icon">${escapeHtml(item.icon)}</span>
                  <div>
                    <strong>${escapeHtml(item.label)}</strong>
                    <p>${escapeHtml(item.hint)}</p>
                  </div>
                </div>
                <span class="workout-launcher-action">开始</span>
              </button>
            `
          )
          .join("")}
      </section>
    </article>
  `;
}

function renderWorkoutSession(profile) {
  const session = getWorkoutSessionStats(profile);
  if (!session) return "";

  return `
    <article class="detail-card workout-session-card">
      <div class="section-title-row">
        <div>
          <span class="dashboard-checkin-kicker">运动中</span>
          <h3>${escapeHtml(session.sport.label)}</h3>
        </div>
        <button class="text-link" data-cancel-workout="1" type="button">放弃</button>
      </div>

      <div class="workout-timer">${escapeHtml(session.timerLabel)}</div>

      <div class="workout-stat-grid">
        <div>
          <span>已运动</span>
          <strong>${escapeHtml(`${session.elapsedMinutes} 分钟`)}</strong>
        </div>
        <div>
          <span>估算卡路里</span>
          <strong>${escapeHtml(`${session.calories} kcal`)}</strong>
        </div>
        <div>
          <span>BMI</span>
          <strong>${escapeHtml(String(getProfileBMI(profile)))}</strong>
        </div>
        <div>
          <span>估算距离</span>
          <strong>${session.distance ? escapeHtml(`${session.distance} km`) : "--"}</strong>
        </div>
      </div>

      <p class="result-tip">系统会根据你的性别、身高、体重和运动类型自动估算消耗，结束后会直接记入打卡。</p>

      <div class="action-row action-row--checkin">
        <button class="mini-button" data-cancel-workout="1" type="button">结束放弃</button>
        <button class="primary-submit" data-finish-workout="1" type="button">结束并打卡</button>
      </div>
    </article>
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
    ${state.workoutSession ? renderWorkoutSession(profile) : renderWorkoutLauncher(profile)}
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
  const bmi = getProfileBMI(profile);
  const heightCm = getProfileHeight(profile);
  const weightKg = getProfileWeight(profile);
  const bodyFat = profile.bodyFat || "--";
  const latestSource = profile.healthSource || "未连接设备";
  const latestSync = profile.deviceSyncedAt || "还没有同步";

  return `
    <article class="detail-card">
      <div class="section-title-row">
        <div>
          <h3>健康概览</h3>
          <p class="result-tip">这里会作为你自己的身体数据中心，后续可衔接智能秤和健康设备。</p>
        </div>
      </div>
      <article class="summary-card summary-card--health">
        <div>
          <span>BMI</span>
          <strong>${escapeHtml(String(bmi))}</strong>
        </div>
        <div>
          <span>身高</span>
          <strong>${heightCm ? escapeHtml(`${heightCm} cm`) : "--"}</strong>
        </div>
        <div>
          <span>体重</span>
          <strong>${weightKg ? escapeHtml(`${weightKg} kg`) : "--"}</strong>
        </div>
      </article>
      <div class="detail-grid">
        <div class="detail-item">
          <span>性别</span>
          <strong>${escapeHtml(profile.gender || "未填写")}</strong>
        </div>
        <div class="detail-item">
          <span>BMI 参考</span>
          <strong>18.5 - 23.9</strong>
        </div>
        <div class="detail-item">
          <span>体脂率</span>
          <strong>${bodyFat === "--" ? "--" : escapeHtml(`${bodyFat}%`)}</strong>
        </div>
        <div class="detail-item">
          <span>数据来源</span>
          <strong>${escapeHtml(latestSource)}</strong>
        </div>
        <div class="detail-item">
          <span>最近同步</span>
          <strong>${escapeHtml(latestSync)}</strong>
        </div>
      </div>
    </article>

    <article class="detail-card">
      <div class="section-title-row">
        <div>
          <h3>外接设备</h3>
          <p class="result-tip">先给你做了智能秤接入口，后续也能继续接 Apple Health、华为运动健康等。</p>
        </div>
      </div>
      <section class="device-list">
        <article class="device-row">
          <div>
            <strong>小米智能秤</strong>
            <p>同步体重、BMI、体脂率与最近一次测量时间</p>
          </div>
          <button class="mini-button mini-button--accent" data-sync-health-device="xiaomi-scale" type="button">模拟导入</button>
        </article>
        <article class="device-row">
          <div>
            <strong>Apple Health</strong>
            <p>后续可同步步数、心率、能量消耗和运动记录</p>
          </div>
          <span class="status-pill">规划中</span>
        </article>
        <article class="device-row">
          <div>
            <strong>华为运动健康</strong>
            <p>预留接口，适合后续接入更多国内设备生态</p>
          </div>
          <span class="status-pill">规划中</span>
        </article>
      </section>
    </article>
  `;
}

function renderPersonalDashboardPage(profile, managedProfiles) {
  const stats = getPersonalDashboard(profile);

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
        <div>
          <strong>${escapeHtml(stats.trainingScore)}</strong>
          <span>练时</span>
        </div>
        <div>
          <strong>${escapeHtml(stats.todayTraining)}</strong>
          <span>今日训练</span>
        </div>
        <div>
          <strong>${escapeHtml(stats.badges)}</strong>
          <span>勋章</span>
        </div>
      </div>

      ${renderCheckinEntry(profile)}
    </article>

    <section class="account-section">
      <div class="section-title-row">
        <h3>我的功能</h3>
        <button class="text-link" data-open-role-picker="1" type="button">切换身份</button>
      </div>
      <div class="account-grid">
        ${renderPersonalShortcutTile("账户", "资料与安全", "账", 'data-open-my-feature="account"')}
        ${renderPersonalShortcutTile("打卡", "记录运动项目", "卡", 'data-open-my-feature="checkin"')}
        ${renderPersonalShortcutTile("订单", "预约记录", "单", 'data-open-my-feature="orders"')}
        ${renderPersonalShortcutTile("关注", "收藏与关注", "关", 'data-open-my-feature="favorites"')}
        ${renderPersonalShortcutTile("积分", `${getProfilePoints(profile, state.bookings || [])} 分`, "分", 'data-open-my-feature="points"')}
        ${renderPersonalShortcutTile("预约", "查看排期", "约", 'data-open-my-feature="schedule"')}
        ${renderPersonalShortcutTile("健康", "BMI 与设备", "健", 'data-open-my-feature="health"')}
        ${renderPersonalShortcutTile("动态", `${profile.posts?.length || 0} 条记录`, "圈", 'data-open-my-feature="moments"')}
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

function renderMyFeaturePage(profile, managedProfiles, feature) {
  const bookings = state.bookings || [];
  const emptyBookingMarkup = '<article class="empty-card">你还没有正式预约。去首页、探索或教练/场馆主页完成第一次预约后，这里才会出现记录。</article>';
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
              <span>身高 / 体重</span>
              <strong>${escapeHtml(`${profile.heightCm || "--"} cm / ${profile.weightKg || "--"} kg`)}</strong>
            </div>
          </div>
        </article>
      `
    },
    checkin: {
      title: "打卡",
      subtitle: "记录跑步、传统力量训练和其他运动项目",
      content: renderCheckinFeature(profile)
    },
    orders: {
      title: "订单",
      subtitle: "查看最近预约、付款与订单状态",
      content: `
        <section class="stack-list">
          ${bookings.length
            ? bookings
                .map(
                  (card) => `
                    <article class="booking-card">
                      <div class="booking-top">
                        <strong>${escapeHtml(card.title)}</strong>
                        <span class="status-pill">${escapeHtml(card.status)}</span>
                      </div>
                      <p>${escapeHtml(card.place)}</p>
                      <div class="community-meta"><span>${escapeHtml(card.price || "待确认")}</span><span>${escapeHtml(card.time)}</span></div>
                    </article>
                  `
                )
                .join("")
            : emptyBookingMarkup}
        </section>
      `
    },
    favorites: {
      title: "收藏",
      subtitle: "这里集中展示你已经关注的用户、教练和健身房",
      content: renderFavoriteProfilesSection()
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
      subtitle: "查看你的课程排期与待上课记录",
      content: `
        <section class="stack-list">
          ${bookings.length
            ? bookings
                .map(
                  (card) => `
                    <article class="booking-card">
                      <div class="booking-top">
                        <strong>${escapeHtml(card.title)}</strong>
                        <span class="status-pill">${escapeHtml(card.status)}</span>
                      </div>
                      <p>${escapeHtml(card.place)}</p>
                      <div class="community-meta"><span>${escapeHtml(card.time)}</span><span>${escapeHtml(card.price || "待确认")}</span></div>
                      <div class="booking-bottom">
                        <span>支持继续测试预约与价格展示</span>
                        <button class="cta" data-go-booking="1" type="button">去订单页</button>
                      </div>
                    </article>
                  `
                )
                .join("")
            : emptyBookingMarkup}
        </section>
      `
    },
    health: {
      title: "健康",
      subtitle: "查看 BMI、身体数据与外接设备同步状态",
      content: renderHealthFeature(profile)
    },
    moments: {
      title: "我的动态",
      subtitle: "按时间从近到远查看你自己发布的健身圈内容",
      content: renderPersonalMoments(profile)
    }
  };

  const currentFeature = featureMap[feature] || featureMap.account;

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

    <article class="helper-card helper-card--my-feature">
      <strong>${escapeHtml(currentFeature.title)}</strong>
      <p>${escapeHtml(currentFeature.subtitle)}</p>
    </article>

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

  if (managed && profile.role === "enthusiast" && profile.id === getMyPageProfile()?.id) {
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
            <button class="mini-button" data-open-city="1" type="button">切换城市</button>
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

function renderWelcomeOverlay() {
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
        <button class="mini-button" data-close-overlay="1" type="button">先看看</button>
      </div>
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
        ${role.fields.map((field) => renderField(field, seed)).join("")}
        <button class="primary-submit" type="submit">提交${role.label}资料</button>
        ${
          state.registerSuccess
            ? `<p class="success-note">${escapeHtml(state.registerSuccess)}</p>`
            : '<p class="helper-note">演示版会直接生成主页；正式版可接入验证码、地图选点、图片上传和审核流。</p>'
        }
      </form>
    </div>
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
                  .map((item) => {
                    if (item.type === "video") {
                      return `
                        <div class="compose-preview-card image-shell image-shell--cover is-loaded">
                          <video class="compose-preview-video" src="${item.url}" controls playsinline preload="metadata"></video>
                          <span class="compose-preview-label">视频</span>
                        </div>
                      `;
                    }

                    return `
                      <div class="compose-preview-card image-shell image-shell--cover is-loaded">
                        <img class="compose-preview-image" src="${item.url}" alt="${escapeHtml(item.name || "预览图")}" loading="lazy" decoding="async">
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

function renderChatOverlay() {
  const targetProfile = getProfile(state.chatTargetProfileId);
  const thread = getThreadForProfile(state.chatTargetProfileId);

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
                  (message) => `
                    <article class="chat-bubble ${message.senderProfileId === state.currentActorProfileId ? "is-self" : ""}">
                      <strong>${escapeHtml(message.senderName)}</strong>
                      <p>${escapeHtml(message.text)}</p>
                      <span>${escapeHtml(message.time)}</span>
                    </article>
                  `
                )
                .join("")
            : '<article class="empty-card">还没有聊天记录，先发一句打招呼吧。</article>'
        }
      </section>

      <form class="chat-form" id="chatForm">
        <input data-chat-input="1" type="text" value="${escapeHtml(state.chatDraft)}" placeholder="输入私信内容，约课或咨询都可以">
        <button class="compose-submit-top" type="submit">发送</button>
      </form>
    </div>
  `;
}

function renderFollowingOverlay() {
  const followedProfiles = getFollowedProfiles();

  return `
    <div class="overlay-backdrop" data-close-overlay="1"></div>
    <div class="overlay-panel overlay-panel--following">
      <div class="overlay-head overlay-head--following">
        <div>
          <p class="page-label">Following</p>
          <h2>我关注的</h2>
          <p>这里会显示你当前设备已经关注的健身房、教练和训练搭子。</p>
        </div>
        <button class="close-button" data-close-overlay="1" type="button">×</button>
      </div>

      <div class="following-tabs">
        <span class="following-tab is-active">已关注</span>
        <span class="following-count">${followedProfiles.length} 个对象</span>
      </div>

      <section class="following-list">
        ${
          followedProfiles.length
            ? followedProfiles
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
                      <button class="follow-button is-active following-action" data-toggle-follow="${profile.id}" type="button">已关注</button>
                    </article>
                  `;
                })
                .join("")
            : `
              <article class="empty-card">
                你还没有关注任何对象。先在探索页上方点几个感兴趣的健身房、教练或用户，这里就会立刻显示出来。
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
  if (state.overlayMode === "city") overlay.innerHTML = renderCityOverlay();
  if (state.overlayMode === "register") overlay.innerHTML = renderRegisterOverlay();
  if (state.overlayMode === "compose") overlay.innerHTML = renderComposeOverlay();
  if (state.overlayMode === "chat") overlay.innerHTML = renderChatOverlay();
  if (state.overlayMode === "following") overlay.innerHTML = renderFollowingOverlay();
  hydrateAsyncImages(overlay);
}

function renderPage() {
  resetProfileSwipe();
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

  if (target.dataset.openFollowing) {
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

  if (target.dataset.openMyHome) {
    openMyPage();
    return;
  }

  if (target.dataset.openMyFeature) {
    const myProfile = getMyPageProfile();
    if (!myProfile) return;
    state.activePage = "profile";
    state.activeProfileId = myProfile.id;
    state.profileSubpage = target.dataset.openMyFeature;
    syncNavActive();
    renderPage();
    appView.scrollTop = 0;
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

  if (target.dataset.likePost) {
    runTask(() => togglePostLike(target.dataset.likePost));
    return;
  }

  if (target.dataset.commentPost) {
    runTask(() => submitPostComment(target.dataset.commentPost));
    return;
  }

  if (target.dataset.openChat) {
    state.chatTargetProfileId = target.dataset.openChat;
    state.chatDraft = "";
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

  if (target.dataset.startWorkout) {
    runTask(() => startWorkoutSession(target.dataset.startWorkout));
    return;
  }

  if (target.dataset.finishWorkout) {
    runTask(() => finishWorkoutSession());
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

  if (target.dataset.toggleFollow) {
    runTask(() => toggleFollow(target.dataset.toggleFollow));
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

  if (target.dataset.registerRole) {
    state.registerRole = target.dataset.registerRole;
    renderOverlay();
    return;
  }

  if (target.dataset.composeProfile) {
    state.composeProfileId = target.dataset.composeProfile;
    renderOverlay();
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

  if (event.target.dataset.composeContent) {
    state.composeContent = event.target.value;
  }

  if (event.target.dataset.chatInput) {
    state.chatDraft = event.target.value;
  }
});

overlay.addEventListener("change", (event) => {
  if (event.target.dataset.composeMediaInput) {
    runTask(async () => {
      const files = Array.from(event.target.files || []).slice(0, 9);
      state.composeMedia = await readMediaFiles(files);
      renderOverlay();
    });
    return;
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
    if (link.dataset.page === "profile") {
      openMyPage();
      return;
    }
    state.profileSubpage = "";
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

syncViewportHeight();
window.addEventListener("resize", syncViewportHeight, { passive: true });
window.addEventListener("orientationchange", syncViewportHeight, { passive: true });

const cachedSnapshot = getStoredSnapshot();
if (cachedSnapshot?.session) {
  syncStateFromServer(cachedSnapshot, { keepOverlay: true });
  state.isBootstrapping = false;
}

renderPage();
refreshSharedState().catch((error) => {
  state.isBootstrapping = false;
  renderPage();
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
