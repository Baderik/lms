<template>
  <div class="scrollable-solution-list">
    <div class="wrapper-for_controll-overflow-list">
      <cv-loading v-if="loading"/>
      <cv-structured-list
        v-else
        class="submit-list"
      >
        <template slot="headings"></template>
        <template slot="items">
          <div
            v-for="event in events" :key="event.id" class="list--item"
            v-bind:class="{ 'list--item--submit': event.type === logEventTypes.TYPE_SUBMIT }"
            v-on:click="elementClickHandler(event)">
            <img
              v-if="event.data.thumbnail"
              :src="event.data.thumbnail"
              class="student--avatar"
              alt='avatar'>
            <div class="one-history-point">
              <span>{{ event.data.message }}</span>
              <component
                :is="iconTrash"
                v-if="logEventTypes.TYPE_MESSAGE === event.type
                && (event.author === userStore.user.id)"
                class="event--delete"
                @click="deleteEvent(event)"/>
              <div
                v-if="logEventTypes.TYPE_SUBMIT === event.type"
                class="checkbox--submit"
                v-bind:class="{ 'hidden': event.submit !== selectedSubmit }">
                <component :is="Checkbox"/>
              </div>
            </div>

          </div>
        </template>
      </cv-structured-list>
    </div>
    <cv-text-input
      v-model.trim="commentary"
      :disabled="false"
      :label="''"
      :light="false"
      :password-visible="false"
      :placeholder="'Введите сообщение'"
      :type="''"
      :value="''"
      class="searchbar"
      v-on:keydown.enter="createMessageHandler">
    </cv-text-input>
    <cv-button @click="sendMessage">click</cv-button>
  </div>
</template>

<script lang="ts">
import LogEventModel from "@/models/LogEventModel";
import * as logEventTypes from '@/models/LogEventModel';
import userStore from '@/store/modules/user';
import TrashCan16 from '@carbon/icons-vue/es/trash-can/16';
import Checkbox16 from '@carbon/icons-vue/es/checkbox--checked--filled/16';
import logEventStore from '@/store/modules/logEvent';
import NotificationMixinComponent from "@/components/common/NotificationMixinComponent.vue";
import { Component, Prop, Watch } from "vue-property-decorator";


@Component({ components: { TrashCan16 } })
export default class LogEventComponent extends NotificationMixinComponent {
  @Prop({ required: true }) problemId!: number;
  @Prop({ required: true }) studentId!: number;
  @Prop({ required: false }) selectedSubmit?: number;
  userStore = userStore;
  logEventStore = logEventStore;
  logEventTypes = logEventTypes;
  loading = true;
  messageIsSending = false;
  commentary = '';
  iconTrash = TrashCan16;
  Checkbox = Checkbox16;
  events: Array<LogEventModel> = [];
  connection!: WebSocket;

  async created() {
    await this.userStore.fetchUserById(this.studentId);
    await this.fetchEvents();
    this.socketConnectionUpdate();
  }

  @Watch('studentId')
  @Watch('problemId')
  onPropChanged() {
    this.fetchEvents();
  }

  socketMessageHandler(event: MessageEvent) {
    debugger;
    console.log('got message via ws');
    console.log(event);

    this.events.push(event.data as LogEventModel);
    this.events.sort((a) => a.id);
  }


  socketEventHandler(event: Event) {
    console.log(event);
  }
  socketErrorHandler(event: Event){
    console.log('something bad happened with sockets');
    console.log(event);
  }

  sendMessage(messageObject: object) {
    this.connection.send(messageObject.toString());
  }

  socketConnectionUpdate() {
    try {
      this.connection.close(1000);
    } catch {
      //
    }
    this.connection = new WebSocket(
      'ws://' + window.location.host
      + `/ws/notifications?user_id=${this.studentId}&problem_id=${this.problemId}`
    );
    this.connection.onmessage = this.socketMessageHandler;
    this.connection.onclose = this.socketEventHandler;
    this.connection.onopen = this.socketEventHandler;
    this.connection.onerror = this.socketErrorHandler;
  }


  async fetchEvents() {
    this.loading = true;
    this.events = await this.logEventStore.fetchLogEventsByProblemAndStudentIds(
      { problem: this.problemId, student: this.studentId },
    );
    await this.thumbnailsUpdate();
    this.loading = false;
  }

  async thumbnailsUpdate() {
    if (!this.events.length)
      return;
    await this.fetchThumbnailForEvent(this.events[0]);
    let previous = this.events[0];
    for (const event of this.events) {
      if (previous.author !== event.author)
        await this.fetchThumbnailForEvent(this.events[0]);
      previous = event;
    }

  }

  async fetchThumbnailForEvent(event: LogEventModel) {
    if (!event.author)
      return
    const user = await this.userStore.fetchUserById(event.author);
    event.data.thumbnail = user.thumbnail;
  }

  elementClickHandler(element: LogEventModel): void {
    if (logEventTypes.TYPE_SUBMIT === element.type)
      this.$emit('submit-selected', { id: element.submit });
    if (logEventTypes.TYPE_CATS_ANSWER === element.type)
      this.$emit('cats-answer', { id: element.submit });
  }

  async mounted() {
    const submits = [...document.getElementsByClassName("submit-list")];
    submits.forEach(element => element.scrollTop = element.scrollHeight);
  }

  async deleteEvent(event: LogEventModel) {
    await this.logEventStore.deleteEvent(event.id);
    this.events = this.events.filter(value => value.id !== event.id);
    await this.thumbnailsUpdate();
  }

  async createMessageHandler() {
    this.messageIsSending = true;
    const newMessage: LogEventModel = {
      ...this.logEventStore.getNewLogEventMessage,
      problem: this.problemId, student: this.studentId,
      data: { message: this.commentary },
    };
    const answer = await this.logEventStore.createLogEvent(newMessage);
    if (answer !== undefined) {
      await this.fetchThumbnailForEvent(answer);
      this.events.push(answer);
    }
    this.commentary = '';
    this.messageIsSending = false;
  }
}

</script>

<style scoped lang="stylus">


.avatar
  width 2em
  margin-bottom 0.3em

.list--item--submit
  span
    font-weight bold

.hidden
  display none

.list--item
  border none
  cursor pointer
  padding-top 0.1em
  padding-bottom 0.1em
  position relative

  .student--avatar
    margin 0
    margin-right 1em
    float left
    height 32px
    width 32px
    border-radius: 150%
    position absolute
    z-index 1

  .event--delete
    display none
    right -1px
    top -1px
    background white
    height 22px
    width 22px
    position absolute

  &:hover
    background-color #e5e5e5

    .event--delete
      display unset

.stuff
  margin-left 1em

.checkbox--submit
  position absolute
  height 16px
  width 16px
  right 3px
  top 50%
  transform translate(-50%, -50%)
  vertical-align center

.searchbar
  position relative
  height 2em
  left 0
  width 100%
  margin-left auto
  margin-right auto
  text-align center

.one-history-point
  word-break break-after
  font-size 1em
  padding 5px
  margin 20px
  background white
  border 1px solid rgba(0, 0, 0, 0.3)
  border-radius 5px
  min-height 40px
  overflow-wrap anywhere
  position relative

.bx--tile.submit-list
  border-left 1em
  padding-left 1em
  margin-left 1em
  box-shadow -1em black

.bx--list
  list-style-type none

.submit-list
  margin 0
  padding 0
  bottom 0
  list-style-type none
  border-radius 10px
  border-color black

.wrapper-for_controll-overflow-list
  height 24.55em
  overflow scroll
  overflow-x hidden
</style>
