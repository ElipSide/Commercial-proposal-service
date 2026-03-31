const I18N = {
  lang: 'ru',
  dict: {},

  async load(lang, page) {
    this.lang = lang;

    const res = await fetch(`/off_bot/static/js/locales/${lang}/${page}.json`);
    this.dict = await res.json();
  },

  t(key) {
    return this.dict[key] ?? key;
  }
};
