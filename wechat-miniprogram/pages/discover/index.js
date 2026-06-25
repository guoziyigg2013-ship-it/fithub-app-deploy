const api = require("../../utils/api");

Page({
  data: {
    loading: true,
    recommendations: [],
    feed: []
  },

  onShow() {
    this.load();
  },

  async load() {
    try {
      const payload = await api.bootstrap();
      const profile = api.currentProfile(payload);
      const follows = new Set(payload.followSet || []);
      const favoritePostIds = new Set(payload.favoritePostIds || []);
      const recommendations = (payload.profiles || [])
        .filter((item) => item.listed && item.id !== (profile && profile.id) && !follows.has(item.id))
        .slice(0, 12);
      this.setData({
        loading: false,
        recommendations,
        feed: api.followedFeed(payload).map((item) => ({
          ...item,
          post: {
            ...item.post,
            favoritedByCurrentActor: favoritePostIds.has(item.post.id)
          }
        }))
      });
    } catch (error) {
      this.setData({ loading: false });
      api.toast(error.message);
    }
  },

  goPublish() {
    wx.navigateTo({ url: "/pages/publish/index" });
  },

  async follow(event) {
    const targetProfileId = event.currentTarget.dataset.id;
    const previousRecommendations = this.data.recommendations;
    const previousFeed = this.data.feed;
    const target = previousRecommendations.find((item) => item.id === targetProfileId);
    const optimisticPosts = target
      ? (target.posts || []).map((post) => ({
          profile: target,
          post: { ...post }
        }))
      : [];
    const mergedFeed = [...previousFeed, ...optimisticPosts]
      .filter((item, index, list) => list.findIndex((candidate) => candidate.post.id === item.post.id) === index)
      .sort((a, b) => String(b.post.createdAt || "").localeCompare(String(a.post.createdAt || "")))
      .slice(0, 30);
    this.setData({
      recommendations: previousRecommendations.filter((item) => item.id !== targetProfileId),
      feed: mergedFeed
    });
    try {
      await api.post("/follow/toggle", {
        targetProfileId,
        desiredFollowing: true,
        compact: true
      });
      api.toast("已关注");
    } catch (error) {
      this.setData({
        recommendations: previousRecommendations,
        feed: previousFeed
      });
      api.toast(error.message);
    }
  },

  applyOptimisticPostMutation(postId, mutatePost) {
    this.setData({
      feed: this.data.feed.map((item) => {
        if (item.post.id !== postId) return item;
        return {
          ...item,
          post: mutatePost({ ...item.post })
        };
      })
    });
  },

  mergeConfirmedPost(postId, confirmedPost) {
    if (!confirmedPost) return;
    this.applyOptimisticPostMutation(postId, (post) => ({
      ...post,
      ...confirmedPost,
      favoritedByCurrentActor:
        typeof confirmedPost.favoritedByCurrentActor === "boolean"
          ? confirmedPost.favoritedByCurrentActor
          : post.favoritedByCurrentActor
    }));
  },

  async like(event) {
    const postId = event.currentTarget.dataset.id;
    const previousFeed = this.data.feed;
    this.applyOptimisticPostMutation(postId, (post) => {
      const liked = !post.likedByCurrentActor;
      return {
        ...post,
        likedByCurrentActor: liked,
        likeCount: Math.max(0, Number(post.likeCount || 0) + (liked ? 1 : -1))
      };
    });
    try {
      const payload = await api.post("/post/like", { postId, compact: true });
      this.mergeConfirmedPost(postId, payload.post);
    } catch (error) {
      this.setData({ feed: previousFeed });
      api.toast(error.message);
    }
  },

  async favorite(event) {
    const postId = event.currentTarget.dataset.id;
    const previousFeed = this.data.feed;
    this.applyOptimisticPostMutation(postId, (post) => {
      const favorited = !post.favoritedByCurrentActor;
      return {
        ...post,
        favoritedByCurrentActor: favorited,
        favoriteCount: Math.max(0, Number(post.favoriteCount || 0) + (favorited ? 1 : -1))
      };
    });
    try {
      const payload = await api.post("/post/favorite-toggle", { postId, compact: true });
      this.mergeConfirmedPost(postId, {
        ...(payload.post || {}),
        favoritedByCurrentActor: (payload.favoritePostIds || []).includes(postId)
      });
    } catch (error) {
      this.setData({ feed: previousFeed });
      api.toast(error.message);
    }
  },

  async report(event) {
    try {
      await api.post("/report/create", {
        targetType: "post",
        targetId: event.currentTarget.dataset.id,
        reason: "不适内容",
        compact: true
      });
      api.toast("已收到举报");
    } catch (error) {
      api.toast(error.message);
    }
  }
});
