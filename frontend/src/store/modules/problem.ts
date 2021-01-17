import ProblemModel from '@/models/ProblemModel';
import axios from 'axios';
import { Action, Module, Mutation, VuexModule } from 'vuex-module-decorators';

@Module({ name: 'problem' })
export default class ProblemModule extends VuexModule {

  _problems: Array<ProblemModel> = [];

  get problems(): Array<ProblemModel> {
    return this._problems;
  }

  @Mutation
  setProblems(payload: Array<ProblemModel>) {
    this._problems = payload;
  }

  @Action
  async fetchProblems() {
    await axios.get('http://localhost:8000/api/problem/')
      .then(response => {
        this.setProblems(response.data);
      })
      .catch(error => {
        console.log(error);
      })
  }

  @Mutation
  addProblemToArray(element: ProblemModel) {
    this._problems.push(element);
    this._problems = [...this._problems];
  }

  private _currentProblem: ProblemModel = this.getNewProblem;

  @Mutation
  setCurrentProblem(problem: ProblemModel) {
    this._currentProblem = { ...problem };
  }

  get currentProblem(): ProblemModel {
    return this._currentProblem;
  }

  get getNewProblem(): ProblemModel {
    return {
      id: NaN, lesson: NaN, type: 'CW', name: '', description: '',
      completed: false, manual: false, language: null,
    };
  }

  @Action
  async fetchProblemById(problemId: number): Promise<ProblemModel> {
    let answer = { data: {} };
    await axios.get(`http://localhost:8000/api/problem/${problemId}/`)
      .then(response => answer = response)
      .catch(error => {
        console.log(error);
      })
    return answer.data as ProblemModel;
  }
}